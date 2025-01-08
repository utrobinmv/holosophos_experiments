# Based on https://github.com/jonatasgrosman/findpapers/blob/master/findpapers/searchers/arxiv_searcher.py
# https://info.arxiv.org/help/api/user-manual.html

import yaml
from typing import Optional, Literal, List, Dict, Any

import requests
import xmltodict


BASE_URL = "http://export.arxiv.org"
URL_TEMPLATE = "{base_url}/api/query?search_query={query}&start={start}&sortBy={sort_by}&sortOrder={sort_order}&max_results={limit}"
SORT_BY_OPTIONS = ("relevance", "lastUpdatedDate", "submittedDate")
SORT_ORDER_OPTIONS = ("ascending", "descending")
KEYS = ("id", "updated", "published", "title", "summary", "author")


def _fix_query(query: str) -> str:
    transformed_query: str = query.replace(" AND NOT ", " ANDNOT ")
    transformed_query = transformed_query.replace("-", " ")
    if transformed_query[0] == '"':
        transformed_query = " " + transformed_query
    return transformed_query


def _format_entries(entries: List[Dict[str, Any]], start_index: int) -> str:
    final_entries = []
    for entry_num, entry in enumerate(entries):
        for key in list(entry.keys()):
            if key not in KEYS:
                entry.pop(key)
        summary = entry["summary"]
        summary = " ".join([l for l in summary.split("\n") if l.strip()])
        entry["summary"] = summary
        entry["id"] = entry["id"].split("/")[-1]
        entry = {k: entry[k] for k in KEYS}
        entry_dump: str = yaml.dump(entry, sort_keys=False, width=10000)
        final_entries.append(f"==== Entry {start_index + entry_num} ====\n" + entry_dump)
    return "\n".join(final_entries)


def arxiv_search(
    query: str,
    offset: Optional[int] = 0,
    limit: Optional[int] = 5,
    sort_by: Optional[str] = "relevance",
    sort_order: Optional[str] = "descending",
) -> str:
    """
    A tool that searches papers in Arxiv.
    It returns text representation that includes meta-information including summary.

    Args:
        query: The search query, required.
        offset: The offset in search results. For instance, if it is 10, first 10 items will be skipped.
        limit: The maximum number of items that will be returned.
        sort_by: 3 possible options to sort by: relevance, lastUpdatedDate, submittedDate
        sort_order: 2 possible sort orders: ascending, descending
    """

    if not isinstance(query, str):
        return "Error: Your search query must be a string"
    if sort_by not in SORT_BY_OPTIONS:
        return f"Error: sort_by should be one of {SORT_BY_OPTIONS}"
    if sort_order not in SORT_ORDER_OPTIONS:
        return f"Error: sort_order should be one of {SORT_ORDER_OPTIONS}"

    url = URL_TEMPLATE.format(
        base_url=BASE_URL,
        query=_fix_query(query),
        start=offset,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    response = requests.get(url)
    content = response.content
    parsed_content = xmltodict.parse(content)

    feed = parsed_content.get("feed", {})
    total_results = int(feed.get("opensearch:totalResults", {}).get("#text", 0))
    start_index = int(feed.get("opensearch:startIndex", {}).get("#text", 0))
    entries = feed.get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    formatted_entries = _format_entries(entries, start_index=start_index)
    return f"Total results: {total_results}\nOffset: {offset}\n{formatted_entries}"
