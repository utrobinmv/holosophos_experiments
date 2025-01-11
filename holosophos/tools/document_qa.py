from smolagents.tools import Tool  # type: ignore
from smolagents.models import Model  # type: ignore


SYSTEM_PROMPT = "You are a helpful assistant that answers questions about documents accurately and concisely."
PROMPT = """Please answer the following question based solely on the provided document.
If there is no answer in the document, output "There is no answer in the provided document".
First cite ALL relevant document fragments, then provide a final answer.
Make sure that you answer the actual question, and not some other similar question.

Question:
{question}

Document:
==== BEGIN DOCUMENT ====
{document}
==== END DOCUMENT ====

Question (repeated):
{question}

Your citations and answer:"""

DESCRIPTION = """
Answer questions about a document.
Use this function when you need to find relevant information in a big document.
It takes a question and a document as inputs and generates an answer based on the document.

Example:
    >>> document = "The quick brown fox jumps over the lazy dog."
    >>> answer = document_qa("What animal is mentioned?", document)
    >>> print(answer)
    "The document mentions two animals: a fox and a dog."

Returns an answer to the question based on the document content.
"""


class DocumentQATool(Tool):  # type: ignore
    name = "document_qa"
    description = DESCRIPTION
    inputs = {
        "question": {
            "type": "string",
            "description": "The question to be answered about the document.",
        },
        "document": {
            "type": "string",
            "description": "The full text of the document to analyze.",
        },
    }
    output_type = "string"

    def __init__(self, model: Model):
        self.model = model
        super().__init__()

    def forward(self, question: str, document: str) -> str:
        if not question.strip() or not document.strip():
            raise ValueError("Both question and document must be non-empty strings")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": PROMPT.format(question=question, document=document),
            },
        ]

        try:
            response: str = self.model(messages)
            return response.strip()
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
