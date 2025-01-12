from smolagents.tools import Tool  # type: ignore
from smolagents.models import Model  # type: ignore


SYSTEM_PROMPT = "You are a helpful assistant that answers questions about documents accurately and concisely."
PROMPT = """Please answer the following questions based solely on the provided document.
If there is no answer in the document, output "There is no answer in the provided document".
First cite ALL relevant document fragments, then provide a final answer.
Answer all given questions one by one.
Make sure that you answer the actual questions, and not some other similar questions.

Questions:
{questions}

Document:
==== BEGIN DOCUMENT ====
{document}
==== END DOCUMENT ====

Questions (repeated):
{questions}

Your citations and answers:"""

DESCRIPTION = """
Answer questions about a document.
Use this function when you need to find relevant information in a big document.
It takes questions and a document as inputs and generates an answer based on the document.

Example:
    >>> document = "The quick brown fox jumps over the lazy dog."
    >>> answer = document_qa("What animal is mentioned? How many of them?", document)
    >>> print(answer)
    "The document mentions two animals: a fox and a dog. 2 animals."

Returns an answer to all questions based on the document content.
"""


class DocumentQATool(Tool):  # type: ignore
    name = "document_qa"
    description = DESCRIPTION
    inputs = {
        "questions": {
            "type": "string",
            "description": "Questions to be answered about the document.",
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

    def forward(self, questions: str, document: str) -> str:
        if not questions.strip() or not document.strip():
            raise ValueError("Both questions and document must be non-empty strings")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": PROMPT.format(questions=questions, document=document),
            },
        ]

        try:
            response = self.model(messages)
            if isinstance(response, str):
                return response.strip()
            final_response: str = response.content.strip()
            return final_response
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
