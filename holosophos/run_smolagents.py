from smolagents import CodeAgent, load_tool
from smolagents.models import LiteLLMModel

from holosophos.tools import convert_tool_to_smolagents, arxiv_search, arxiv_download

search_tool = convert_tool_to_smolagents(arxiv_search)
download_tool = convert_tool_to_smolagents(arxiv_download)
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-20240620")
agent = CodeAgent(tools=[search_tool, download_tool], model=model, add_base_tools=False)
agent.run("Какая лучшая модель согласно role-play бенчмарку Ильи Гусева?")
