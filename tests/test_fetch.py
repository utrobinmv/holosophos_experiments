from holosophos.tools.fetch import fetch


def test_fetch() -> None:
    result = fetch("https://github.com/IlyaGusev/")
    assert "pingpong" in result
