from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool, VisitWebpageTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    arxiv_search_tool,
    arxiv_download_tool,
    text_editor_tool,
    DocumentQATool,
)

NAME = "librarian"
DESCRIPTION = """This agent runs gets and analyzes information from papers.
It has access to ArXiv and web search.
Give it your task as an argument."""


def get_librarian_agent(
    model: Model,
    max_steps: int = 50,
    planning_interval: Optional[int] = 4,
    max_print_outputs_length: int = 20000,
) -> CodeAgent:
    return CodeAgent(
        name=NAME,
        description=DESCRIPTION,
        tools=[
            arxiv_search_tool,
            arxiv_download_tool,
            text_editor_tool,
            DocumentQATool(model),
            DuckDuckGoSearchTool(),
            VisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("librarian"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
    )
