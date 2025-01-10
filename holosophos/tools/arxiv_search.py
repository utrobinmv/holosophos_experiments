# Based on https://github.com/jonatasgrosman/findpapers/blob/master/findpapers/searchers/arxiv_searcher.py
# https://info.arxiv.org/help/api/user-manual.html

import yaml
from typing import Optional, Literal, List, Dict, Any, Union
from datetime import datetime

import requests
import xmltodict
from jinja2 import Template


BASE_URL = "http://export.arxiv.org"
URL_TEMPLATE = "{base_url}/api/query?search_query={query}&start={start}&sortBy={sort_by}&sortOrder={sort_order}&max_results={limit}"
SORT_BY_OPTIONS = ("relevance", "lastUpdatedDate", "submittedDate")
SORT_ORDER_OPTIONS = ("ascending", "descending")
KEYS = ("id", "updated", "published", "title", "summary", "author")


def _format_id(url: str) -> str:
    return url.split("/")[-1]


def _format_text_field(text: str) -> str:
    text = " ".join([l.strip() for l in text.split() if l.strip()])
    return text


def _format_authors(authors: Union[List[Dict[str, str]], Dict[str, str]]) -> str:
    if not authors:
        return ""
    if isinstance(authors, dict):
        authors = [authors]
    names = [author["name"] for author in authors]
    result = ", ".join(names[:3])
    if len(names) > 3:
        result += " et al."
    return result


def _format_categories(categories: Union[List[Dict[str, Any]], Dict[str, Any]]) -> str:
    if not categories:
        return ""
    if isinstance(categories, dict):
        categories = [categories]
    clean_categories = [c.get("@term", "") for c in categories]
    clean_categories = [c.strip() for c in clean_categories if c.strip()]
    return ", ".join(clean_categories)


def _format_date(date: str) -> str:
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%B %d, %Y")


def _clean_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": _format_id(entry["id"]),
        "title": _format_text_field(entry["title"]),
        "authors": _format_authors(entry["author"]),
        "summary": _format_text_field(entry["summary"]),
        "published": _format_date(entry["published"]),
        "updated": _format_date(entry["updated"]),
        "categories": _format_categories(entry.get("category", {})),
        "comment": _format_text_field(entry.get("arxiv:comment", {}).get("#text", "")),
    }


ENTRY_TEMPLATE = """==== Entry {{index}} ====
Paper ID: {{entry["id"]}}
Title: {{entry["title"]}}
Authors: {{entry["authors"]}}
Summary: {{entry["summary"]}}{% if entry["comment"] %}
Comment: {{entry["comment"]}}{% endif %}
Publication date: {{entry["published"]}}{% if entry["published"] != entry["updated"] %}
Date of last update: {{entry["updated"]}}{% endif %}
Categories: {{entry["categories"]}}"""


def _fix_query(query: str) -> str:
    transformed_query: str = query.replace(" AND NOT ", " ANDNOT ")
    transformed_query = transformed_query.replace("-", " ")
    if transformed_query[0] == '"':
        transformed_query = " " + transformed_query
    return transformed_query


def _format_entries(entries: List[Dict[str, Any]], start_index: int) -> str:
    final_entries = []
    for entry_num, entry in enumerate(entries):
        index = start_index + entry_num
        template = Template(ENTRY_TEMPLATE)
        fixed_entry = _clean_entry(entry)
        final_entries.append(
            template.render(
                index=index,
                entry=fixed_entry,
            )
        )
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
    It returns text representation that includes meta-information about the papers with theirs summaries.
    To search one of the entry fields prepend the field prefix followed by a colon to the search term.

    The following prefixes can be searched:
    - ti / Title
    - au / Author
    - abs / Abstract
    - cat / Subject Category
    - id / Id
    - submittedDate / Date, expected format: [YYYYMMDDTTTT+TO+YYYYMMDDTTTT]

    The API allows advanced query construction with Boolean operators.
    The following operators can be used: AND, OR, ANDNOT

    Query to find articles by the author Adrian Del Maestro: au:del_maestro
    Query with dates: au:del_maestro&submittedDate:[202301010600+TO+202401010600]
    Query to find articles by the author Adrian DelMaestro with word "checkerboard" in the title:
    au:del_maestro+AND+ti:checkerboard

    Args:
        query: The search query, required.
        offset: The offset in search results. For instance, if it is 10, first 10 items will be skipped.
        limit: The maximum number of items that will be returned.
        sort_by: 3 possible options to sort by: relevance, lastUpdatedDate, submittedDate
        sort_order: 2 possible sort orders: ascending, descending
    """

    assert isinstance(query, str), "Error: Your search query must be a string"
    assert isinstance(offset, int), "Error: offset should be an integer"
    assert isinstance(limit, int), "Error: limit should be an integer"
    assert isinstance(sort_by, str), "Error: sort_by should be a string"
    assert isinstance(sort_order, str), "Error: sort_order should be a string"
    assert query.strip(), "Error: Your query should not be empty"
    assert (
        sort_by in SORT_BY_OPTIONS
    ), f"Error: sort_by should be one of {SORT_BY_OPTIONS}"
    assert (
        sort_order in SORT_ORDER_OPTIONS
    ), f"Error: sort_order should be one of {SORT_ORDER_OPTIONS}"
    assert offset >= 0, "Error: offset must be 0 or positive number"
    assert limit < 100, "Error: limit is too large, it should be less than 100"
    assert limit > 0, "Error: limit should be greater than 0"

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
