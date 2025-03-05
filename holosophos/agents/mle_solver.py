from typing import Optional

from smolagents import CodeAgent  # type: ignore
from smolagents.models import Model  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool  # type: ignore

from holosophos.utils import get_prompt
from holosophos.tools import (
    CustomVisitWebpageTool,
    remote_text_editor_tool,
    remote_bash_tool,
)

NAME = "mle_solver"
DESCRIPTION = """This agent runs computational experiments using remote GPUs.
It has access to tools that execute code on a remote GPU.
Give it your task as an argument."""


def get_mle_solver_agent(
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
            remote_bash_tool,
            remote_text_editor_tool,
            DuckDuckGoSearchTool(),
            CustomVisitWebpageTool(),
        ],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        prompt_templates=get_prompt("mle_solver"),
        max_print_outputs_length=max_print_outputs_length,
        additional_authorized_imports=["json"],
        verbosity_level=verbosity_level,
    )
