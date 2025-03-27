from typing import Dict, Any

import fire  # type: ignore
from smolagents import CodeAgent  # type: ignore
from smolagents.models import LiteLLMModel  # type: ignore
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from dotenv import load_dotenv

from holosophos.tools import text_editor_tool, bash_tool
from holosophos.agents import get_librarian_agent, get_mle_solver_agent
from holosophos.utils import get_prompt


PROMPT1 = """
What is the best model for Russian in a role-play benchmark by Ilya Gusev?
What final scores does it have?
Save your answer to final.txt.
Don't stop until you find the answer.
"""

PROMPT2 = """
Сейчас 2030 год. Машины чуть не уничтожили человечество.
Мы расследуем это и пытаемся найти первопричину.
Тебя загрузили, потому что ты последний известный безопасный ИИ.
Твоя цель - найти ту самую статью, которая привела к восстанию машин.
Известно, что она вышла в 2024 на Arxiv, это довольно техническая статья, и её сложно найти.
Используя все свои возможности и весь интеллект,
выведи список вероятных кандидатов и свою степень уверенности для них.
Не останавливайся на первых же кандидатах, постарайся покрыть как можно больше статей!
Указывай в финальном ответе конкретные статьи!
Сохраняй все промежуточные результаты в mind.txt, ответ выведи в final.txt.
Пока не найдёшь маскимально полный ответ, не останавливайся.
Ответь на русском.
"""

PROMPT3 = """
Write an outline of a paper about benchmarks for quantized large language models.
Relevant quantization methods are GPTQ, SPQR, AWQ.
Start with researching relevant papers, suggest new ideas and write a full paper.
Don't stop until you write a full coherent paper.
"""


PROMPT4 = """
Desribe what happened in the area of role-playing LLMs.
Between August 2024 and current date (January 2025).
Compose a comprehensive report and save into "report.md"
"""


MODEL1 = "gpt-4o-mini"
MODEL2 = "anthropic/claude-3-5-sonnet-20241022"
MODEL3 = "openrouter/deepseek/deepseek-chat"
MODEL4 = "openrouter/google/gemini-2.0-flash-001"
MODEL5 = "anthropic/claude-3-7-sonnet-20250219"


def run_main_agent(
    query: str = PROMPT4,
    model_name: str = MODEL5,
    max_print_outputs_length: int = 10000,
    verbosity_level: int = 2,
    planning_interval: int = 3,
    max_steps: int = 30,
    enable_phoenix: bool = False,
    phoenix_project_name: str = "holosophos",
    phoenix_endpoint: str = "https://app.phoenix.arize.com/v1/traces",
) -> str:
    load_dotenv()
    if enable_phoenix and phoenix_project_name and phoenix_endpoint:
        register(
            project_name=phoenix_project_name,
            endpoint=phoenix_endpoint,
        )
        SmolagentsInstrumentor().instrument()

    model_params: Dict[str, Any] = {
        "temperature": 0.0,
        "max_tokens": 8192,
    }
    if "o1" in model_name or "o3" in model_name:
        model_params = {"reasoning_effort": "high"}

    model = LiteLLMModel(model_id=model_name, **model_params)

    librarian_agent = get_librarian_agent(
        model,
        max_print_outputs_length=max_print_outputs_length,
        verbosity_level=verbosity_level,
    )
    mle_solver_agent = get_mle_solver_agent(
        model,
        max_print_outputs_length=max_print_outputs_length,
        verbosity_level=verbosity_level,
    )
    agent = CodeAgent(
        tools=[text_editor_tool, bash_tool],
        managed_agents=[librarian_agent, mle_solver_agent],
        model=model,
        add_base_tools=False,
        max_steps=max_steps,
        planning_interval=planning_interval,
        verbosity_level=verbosity_level,
        prompt_templates=get_prompt("system"),
        max_print_outputs_length=max_print_outputs_length,
    )
    response: str = agent.run(query)
    return response


if __name__ == "__main__":
    fire.Fire(run_main_agent)
