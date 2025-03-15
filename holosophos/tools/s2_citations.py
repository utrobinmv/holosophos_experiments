# Based on
# https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_get_paper_citations

import json
from typing import Optional, List, Dict, Any
from urllib3.util.retry import Retry
import time
import random

import requests

OLD_API_URL_TEMPLATE = "https://api.semanticscholar.org/v1/paper/{paper_id}"
GRAPH_URL_TEMPLATE = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields={fields}&offset={offset}&limit={limit}"
FIELDS = "title,authors,externalIds,venue,citationCount,publicationDate"

WORKING_PROXIES_FILE = "working_proxies.json"
with open(WORKING_PROXIES_FILE, "r") as f:
        PROXIES_LIST = json.load(f)

a = 1

def _get_results(url: str, proxies: Optional[Dict[str, str]] = None) -> requests.Response:
    retry_strategy = Retry(
        total=1,
        backoff_factor=30,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    try:
        time.sleep(random.uniform(1, 3))
        response = session.get(url, timeout=30, proxies=proxies)
        response.raise_for_status()
        return response
    except (
        requests.exceptions.ConnectionError,
        requests.exceptions.RequestException,
        requests.exceptions.HTTPError,
        requests.exceptions.ProxyError,
    ) as e:
        print(f"Failed after {retry_strategy.total} retries: {str(e)}")
        print(f"Proxy failed: {proxies}. Error: {str(e)}")
        raise

    return response


def _format_authors(authors: List[Dict[str, Any]]) -> List[str]:
    return [a["name"] for a in authors]


def _clean_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry = entry["citingPaper"]
    external_ids = entry.get("externalIds")
    if not external_ids:
        external_ids = dict()
    external_ids.pop("CorpusId", None)
    arxiv_id = external_ids.pop("ArXiv", None)
    return {
        "arxiv_id": arxiv_id,
        "external_ids": external_ids if external_ids else None,
        "title": entry["title"],
        "authors": _format_authors(entry["authors"]),
        "venue": entry.get("venue", ""),
        "citation_count": entry.get("citationCount", 0),
        "publication_date": entry.get("publicationDate", ""),
    }


def _format_entries(
    entries: List[Dict[str, Any]],
    start_index: int,
    total_results: int,
) -> str:
    clean_entries = [_clean_entry(e) for e in entries]
    return json.dumps(
        {
            "total_count": total_results,
            "returned_count": len(entries),
            "offset": start_index,
            "results": clean_entries,
        },
        ensure_ascii=False,
    )


def s2_citations(
    arxiv_id: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 50,
) -> str:
    """
    Get all papers that cited a given arXiv paper based on Semantic Scholar info.

    Returns a JSON object serialized to a string. The structure is:
    {"total_count": ..., "returned_count": ..., "offset": ..., "results": [...]}
    Every item in the "results" has the following fields:
    ("arxiv_id", "external_ids", "title", "authors", "venue", "citation_count", "publication_date")
    Use `json.loads` to deserialize the result if you want to get specific fields.

    Args:
        arxiv_id: The ID of a given arXiv paper.
        offset: The offset to scroll through citations. 10 items will be skipped if offset=10. 0 by default.
        limit: The maximum number of items to return. limit=50 by default.
    """

    assert isinstance(arxiv_id, str), "Error: Your arxiv_id must be a string"
    if "v" in arxiv_id:
        arxiv_id = arxiv_id.split("v")[0]
    paper_id = f"arxiv:{arxiv_id}"

    url = GRAPH_URL_TEMPLATE.format(
        paper_id=paper_id, fields=FIELDS, offset=offset, limit=limit
    )

    # Попробуем каждый прокси из списка
    for proxy in PROXIES_LIST:
        try:    
            response = _get_results(url, proxies=proxy)
            result = response.json()
            entries = result["data"]
            total_count = len(result["data"]) + result["offset"]

            if "next" in result:
                paper_url = OLD_API_URL_TEMPLATE.format(paper_id=paper_id)
                paper_response = _get_results(paper_url, proxies=proxy)
                paper_result = paper_response.json()
                total_count = paper_result["numCitedBy"]

            return _format_entries(entries, offset if offset else 0, total_count)

        except Exception as e:
            print(f"Proxy failed: {proxy}. Error: {str(e)}")
            continue

    raise Exception("All proxies failed. Please check your proxy list or try again later.")
