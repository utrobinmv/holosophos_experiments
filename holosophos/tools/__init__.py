from typing import Callable, Any

from smolagents.tools import tool, Tool  # type: ignore

from holosophos.tools.arxiv_search import arxiv_search
from holosophos.tools.arxiv_download import arxiv_download
from holosophos.tools.bash import bash


def convert_tool_to_smolagents(function: Callable[..., Any]) -> Tool:
    return tool(function)


__all__ = [
    "arxiv_search",
    "arxiv_download",
    "convert_tool_to_smolagents",
    "bash",
]
