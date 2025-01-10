from typing import Optional

from trafilatura import fetch_url, extract


def fetch(url: str, max_chars_count: Optional[int] = 5000) -> str:
    """
    The tool to get text content from web pages with a given URL.
    Args:
        url: Url of the page
        max_chars_count: The number of first characters to return
    """
    downloaded = fetch_url(url)
    result = extract(downloaded)
    if result is None:
        return f"Failed to fetch content from url: {url}"
    text: str = result[:max_chars_count]
    return text
