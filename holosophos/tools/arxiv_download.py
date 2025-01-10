from pathlib import Path

import requests
from pdfminer.high_level import extract_text


MARKER_API_URL = "http://localhost:5001/{}"
DIR_PATH = Path(__file__).parent
ROOT_PATH = DIR_PATH.parent.parent
WORKSPACE_DIR = ROOT_PATH / "workdir"


def convert_pdf_to_md(pdf_path: Path, md_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)

    status_code = None
    try:
        response = requests.get(MARKER_API_URL.format("health"))
        status_code = response.status_code
    except Exception:
        pass

    if status_code != 200:
        with md_path.open("w") as w:
            w.write(extract_text(str(pdf_path.resolve())))
        return
    with pdf_path.open("rb") as pdf_file:
        files = {"pdf_file": (pdf_path.name, pdf_path.open("rb"), "application/pdf")}
        response = requests.post(MARKER_API_URL.format("convert"), files=files)
    response.raise_for_status()
    result = response.json()
    markdown_text = result["result"]["markdown"]
    md_path.write_text(markdown_text, encoding="utf-8")


def arxiv_download(paper_id: str) -> str:
    """
    A tool that downloads papers from Arxiv and converts them to text.

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
    md_output_filename = WORKSPACE_DIR / f"{paper_id}.md"
    text = ""
    if not md_output_filename.exists():
        convert_pdf_to_md(pdf_output_filename, md_output_filename)
    with open(md_output_filename.resolve()) as r:
        text = r.read()
    return text
