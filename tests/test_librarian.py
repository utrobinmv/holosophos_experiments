import re
from typing import Optional

from smolagents import LiteLLMModel  # type: ignore

from holosophos.agents import get_librarian_agent


def extract_first_number(text: str) -> Optional[int]:
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def test_librarian_case1() -> None:
    query = "Which work introduces Point-E, a language-guided DM?"
    #model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    model = LiteLLMModel(model_id="litellm_proxy/Qwen2.5-32B-Instruct-AWQ", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    assert "2212.08751" in str(answer)


def test_librarian_case2() -> None:
    query = "What paper was first to propose generating sign pose sequences from gloss sequences by employing VQVAE?"
    #model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    model = LiteLLMModel(model_id="litellm_proxy/Qwen2.5-32B-Instruct-AWQ", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    assert "2208.09141" in str(answer)


def test_librarian_case3() -> None:
    query = (
        "How many citations does the transformers paper have according to Semantic Scholar? "
        "Return only one number as a string and nothing else."
    )
    #model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    model = LiteLLMModel(model_id="litellm_proxy/Qwen2.5-32B-Instruct-AWQ", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    int_answer = extract_first_number(answer.strip())
    assert int_answer is not None
    assert int_answer > 100000
