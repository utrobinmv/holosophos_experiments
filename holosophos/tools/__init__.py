from typing import Callable, Any

from smolagents.tools import tool, Tool  # type: ignore

from holosophos.tools.arxiv_search import arxiv_search
from holosophos.tools.arxiv_download import arxiv_download
from holosophos.tools.bash import bash
from holosophos.tools.str_replace_editor import str_replace_editor
from holosophos.tools.document_qa import DocumentQATool


def convert_tool_to_smolagents(function: Callable[..., Any]) -> Tool:
    return tool(function)


__all__ = [
    "arxiv_search",
    "arxiv_download",
    "convert_tool_to_smolagents",
    "DocumentQATool",
    "bash",
    "str_replace_editor",
]
