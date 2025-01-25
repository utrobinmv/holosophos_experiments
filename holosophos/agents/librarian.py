from typing import Optional

from smolagents import CodeAgent, ManagedAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool, VisitWebpageTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    arxiv_search_tool,
    arxiv_download_tool,
    text_editor_tool,
    DocumentQATool,
)


DESCRIPTION = """This agent runs gets and analyzes information from papers.
It has access to ArXiv and web search.
Give it your task as an argument."""


def get_librarian_agent(
    model: Model,
    max_steps: int = 50,
    planning_interval: Optional[int] = None,
    max_print_outputs_length: int = 20000,
) -> ManagedAgent:
    agent = CodeAgent(
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
        system_prompt=get_prompt("librarian_system"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
    )

    managed_agent = ManagedAgent(
        agent=agent,
        name="librarian",
        description=DESCRIPTION,
        managed_agent_prompt=get_prompt("librarian_managed"),
    )
    return managed_agent
