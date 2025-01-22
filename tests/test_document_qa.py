from smolagents import LiteLLMModel  # type: ignore

from holosophos.tools import DocumentQATool, arxiv_download


DOCUMENT1 = """
The dominant sequence transduction models are based on complex recurrent or convolutional
neural networks in an encoder-decoder configuration. The best performing models also connect
the encoder and decoder through an attention mechanism. We propose a new simple network architecture,
the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions
entirely. Experiments on two machine translation tasks show these models to be superior in quality
while being more parallelizable and requiring significantly less time to train. Our model achieves
28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results,
including ensembles by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model
establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on
eight GPUs, a small fraction of the training costs of the best models from the literature.
We show that the Transformer generalizes well to other tasks by applying it successfully to
English constituency parsing both with large and limited training data.
"""


def test_document_qa() -> None:
    model = LiteLLMModel(model_id="gpt-4o-mini", temperature=0.0)
    tool = DocumentQATool(model)
    answer = tool(
        questions="What is BLEU on the WMT 2014 English-to-German translation task?",
        document=DOCUMENT1,
    )
    assert "28.4" in answer


def test_real_question() -> None:
    model = LiteLLMModel(model_id="gpt-4o", temperature=0.0)
    tool = DocumentQATool(model)
    questions = "What is the best model for the Russian language according to the role-play benchmark and its final score?"
    document = arxiv_download("2409.06820")
    answer = tool(questions=questions, document=document)
    assert "4.63" in answer or "4.68" in answer
