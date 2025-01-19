from functools import partial

from smolagents import CodeAgent, ManagedAgent  # type: ignore
from smolagents.models import LiteLLMModel  # type: ignore
from smolagents.default_tools import DuckDuckGoSearchTool, VisitWebpageTool  # type: ignore

from holosophos.tools import (
    convert_tool_to_smolagents,
    arxiv_search,
    arxiv_download,
    bash,
    DocumentQATool,
    text_editor,
)
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

MODEL1 = "gpt-4o-mini"
MODEL2 = "anthropic/claude-3-5-sonnet-20241022"

search_tool = convert_tool_to_smolagents(arxiv_search)
download_tool = convert_tool_to_smolagents(arxiv_download)
bash_tool = convert_tool_to_smolagents(bash)
text_editor_tool = convert_tool_to_smolagents(text_editor)

model = LiteLLMModel(model_id=MODEL1, temperature=0.0, max_tokens=8192)
agent = CodeAgent(
    tools=[
        search_tool,
        download_tool,
        bash_tool,
        text_editor_tool,
        DocumentQATool(model),
        DuckDuckGoSearchTool(),
        VisitWebpageTool(),
    ],
    model=model,
    add_base_tools=False,
    max_steps=50,
    planning_interval=3,
    system_prompt=get_prompt("system"),
    max_print_outputs_length=10000,
)
agent.run(PROMPT1)
