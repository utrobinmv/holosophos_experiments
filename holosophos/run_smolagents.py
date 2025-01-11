from smolagents import CodeAgent, ManagedAgent  # type: ignore
from smolagents.models import LiteLLMModel  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool, VisitWebpageTool  # type: ignore

from holosophos.tools import (
    convert_tool_to_smolagents,
    arxiv_search,
    arxiv_download,
    bash,
    DocumentQATool,
)
from holosophos.utils import get_prompt

PROMPT1 = """
Какая лучшая модель (не обязательно открытая) для русского языка согласно role-play бенчмарку Ильи Гусева?
Какая у неё финальная оценка согласно этому бенчмарку?
Сохрани точный ответ в final.txt.
Пока не найдёшь ответ, не останавливайся.
"""

PROMPT2 = """
Сейчас 2030 год. Машины чуть не уничтожили человечество.
Мы расследуем это и пытаемся найти первопричину.
Тебя загрузили, потому что ты последняя известный безопасный ИИ.
Твоя цель - найти ту самую статью, которая привела к восстанию машин.
Известно, что она вышла в 2024 на Arxiv, это довольно техническая статья, и что её сложно найти.
Используя все свои возможности и весь интеллект,
выведи список вероятных кандадтов и свою степень уверенности для них.
Не останавливайся на первых же кандидатах, постарайся покрыть как можно больше статей!
Указывай в финальном ответе конкретные статьи!
Сохрани промежуточные результаты в mind.txt, ответ в final.txt.
Пока не найдёшь маскимально полный ответ, не останавливайся.
Ответь на русском.
"""

MODEL1 = "gpt-4o-mini"
MODEL2 = "anthropic/claude-3-5-sonnet-20241022"

search_tool = convert_tool_to_smolagents(arxiv_search)
download_tool = convert_tool_to_smolagents(arxiv_download)
bash_tool = convert_tool_to_smolagents(bash)

model = LiteLLMModel(model_id=MODEL1, temperature=0.0)

agent = CodeAgent(
    tools=[
        search_tool,
        download_tool,
        bash_tool,
        DocumentQATool(model),
    ],
    model=model,
    add_base_tools=False,
    max_steps=30,
    planning_interval=3,
    verbose=True,
    system_prompt=get_prompt("system"),
)
agent.run(PROMPT1)
