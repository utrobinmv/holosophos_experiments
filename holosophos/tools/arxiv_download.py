# Based on
# https://github.com/SamuelSchmidgall/AgentLaboratory/blob/main/tools.py

from pathlib import Path

import requests
from pypdf import PdfReader


DIR_PATH = Path(__file__).parent
ROOT_PATH = DIR_PATH.parent.parent
WORKSPACE_DIR = ROOT_PATH / "workdir"


def _convert_pdf_to_text(pdf_path: Path, txt_path: Path) -> None:
    # Why not Marker? Because it is too heavy.

    txt_path.parent.mkdir(parents=True, exist_ok=True)

    full_text = ""
    reader = PdfReader(str(pdf_path.resolve()))
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
        except Exception:
            continue
        full_text += f"==== Page {page_number} ====\n{text}\n"
    txt_path.write_text(full_text, encoding="utf-8")


def arxiv_download(paper_id: str) -> str:
    """
    Downloads a paper from Arxiv and converts it to text.

    Returns a text version of the paper.
    Also saves both pdf and txt version of the paper to the work directory.

    Args:
        paper_id: ID of the paper on Arxiv. For instance: 2409.06820v1
    """

    pdf_output_filename = WORKSPACE_DIR / f"{paper_id}.pdf"
    if not pdf_output_filename.exists():
        pdf_url = f"https://arxiv.org/pdf/{paper_id}"
        response = requests.get(pdf_url)
        content_type = response.headers.get("content-type")
        assert content_type
        assert "application/pdf" in content_type.lower()
        with open(pdf_output_filename.resolve(), "wb") as fp:
            fp.write(response.content)
    txt_output_filename = WORKSPACE_DIR / f"{paper_id}.txt"
    if not txt_output_filename.exists():
        _convert_pdf_to_text(pdf_output_filename, txt_output_filename)
    return txt_output_filename.open().read()
