from holosophos.tools import arxiv_search


def test_arxiv_search() -> None:
    result = arxiv_search("PingPong: A Benchmark for Role-Playing Language Models")
    assert "Ilya Gusev" in result
