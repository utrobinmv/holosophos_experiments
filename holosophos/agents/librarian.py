from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    arxiv_search_tool,
    arxiv_download_tool,
    s2_citations_tool,
    DocumentQATool,
    CustomVisitWebpageTool,
)

NAME = "librarian"
DESCRIPTION = """This agent runs gets and analyzes information from papers.
It has access to ArXiv and web search.
Give it your task as an argument."""


def get_librarian_agent(
    model: Model,
    max_steps: int = 21,
    planning_interval: Optional[int] = 5,
    max_print_outputs_length: int = 20000,
    verbosity_level: int = 2,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[
            DuckDuckGoSearchTool(),
            arxiv_search_tool,
            arxiv_download_tool,
            s2_citations_tool,
            DocumentQATool(model),
            CustomVisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("librarian"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
        verbosity_level=verbosity_level,
    )
