from smolagents import CodeAgent, load_tool
from smolagents.models import LiteLLMModel

from holosophos.tools import convert_tool_to_smolagents, arxiv_search, arxiv_download, bash, fetch

search_tool = convert_tool_to_smolagents(arxiv_search)
download_tool = convert_tool_to_smolagents(arxiv_download)
bash_tool = convert_tool_to_smolagents(bash)
fetch_tool = convert_tool_to_smolagents(fetch)
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20241022")
agent = CodeAgent(tools=[search_tool, download_tool, bash_tool], model=model, add_base_tools=False, max_steps=11, planning_interval=3)
agent.run("Какая лучшая модель (не обязательно открытая) для русского языка согласно role-play бенчмарку Ильи Гусева? Какая у неё финальная оценка согласно этому бенчмарку? Сохрани точный ответ в final.txt. Пока не найдёшь ответ, не останавливайся.")
