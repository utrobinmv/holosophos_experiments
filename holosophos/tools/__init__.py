from typing import Callable

from holosophos.tools.arxiv_search import arxiv_search
from holosophos.tools.arxiv_download import arxiv_download


def convert_tool_to_smolagents(function: Callable):
    from smolagents.tools import tool
    return tool(function)


__all__ = ["arxiv_search", "arxiv_download", "convert_tool_to_smolagents"]
