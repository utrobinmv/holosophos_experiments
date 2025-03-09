from smolagents import LiteLLMModel  # type: ignore

from holosophos.agents import get_librarian_agent


def test_librarian_case1() -> None:
    query = "Which work introduces Point-E, a language-guided DM?"
    model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    assert "2212.08751" in str(answer)


def test_librarian_case2() -> None:
    query = "What paper was first to propose generating sign pose sequences from gloss sequences by employing VQVAE?"
    model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    assert "2208.09141" in str(answer)


def test_librarian_case3() -> None:
    query = "How many citations does the transformers paper have according to Semantic Scholar? Return only one number as a string."
    model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    agent = get_librarian_agent(model=model)
    answer = agent(query)
    assert int(answer.strip().split("\n")[-1]) > 100000
