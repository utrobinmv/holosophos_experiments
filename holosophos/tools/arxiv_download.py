import io
from typing import cast

import requests
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


def arxiv_download(paper_id: str) -> str:
    """
    A tool that downloads papers from Arxiv and converts them to text.

    Args:
        paper_id: ID of the paper on Arxiv. For instance: 2409.06820v1
    """

    pdf_output_filename = f"{paper_id}.pdf"
    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    response = requests.get(pdf_url)
    assert "application/pdf" in response.headers.get("content-type").lower()
    with open(pdf_output_filename, "wb") as fp:
        fp.write(response.content)
    md_output_filename = f"{paper_id}.md"
    converter = PdfConverter(artifact_dict=create_model_dict(),)
    rendered = converter(pdf_output_filename)
    text, _, images = text_from_rendered(rendered)
    with open(md_output_filename, "w") as fp:
        fp.write(text)
    return text
