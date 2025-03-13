import re
from typing import Optional

from smolagents import LiteLLMModel  # type: ignore

from holosophos.agents import get_librarian_agent


def extract_first_number(text: str) -> Optional[int]:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None

query = (
    "How many citations does the transformers paper have according to Semantic Scholar? "
    "Return only one number as a string and nothing else."
)

model = LiteLLMModel(model_id="litellm_proxy/Qwen2.5-32B-Instruct-AWQ", temperature=0.0)
agent = get_librarian_agent(model=model)
answer = agent(query)
int_answer = extract_first_number(answer.strip())

print('answer:', answer)