# Based on
# https://github.com/SamuelSchmidgall/AgentLaboratory/blob/main/tools.py

from pathlib import Path
from typing import Any

import requests
import bs4
from markdownify import MarkdownConverter  # type: ignore
from pypdf import PdfReader

from holosophos.files import WORKSPACE_DIR_PATH


class ArxivHTMLConverter(MarkdownConverter):  # type: ignore
    def __init__(self, base_url: str, *args: Any, **kwargs: Any) -> None:
        self.base_url = base_url

        super().__init__(*args, **kwargs)

    def convert_cite(
        self, el: bs4.element.Tag, text: str, convert_as_inline: bool = False
    ) -> str:
        parts = text.split(";")
        new_parts = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            new_part = part
            year = part.split()[-1]
            if len(year) > 4 and year[0] == "(" and year[-1] == ")":
                new_part = f'{" ".join(part.split()[:-1])}, {year[1:-1]}'
            new_parts.append(new_part)
        return f'({"; ".join(new_parts)})'

    def convert_sup(self, *args: Any, **kwargs: Any) -> str:
        return ""

    def convert_span(
        self, el: bs4.element.Tag, text: str, convert_as_inline: bool = False
    ) -> str:
        if "ltx_tag_item" in el["class"]:
            return ""
        if "ltx_note_outer" in el["class"]:
            return f" (Footnote {text})"
        if "ltx_tag_note" in el["class"]:
            return text + ": "
        return text

    def convert_figure(
        self, el: bs4.element.Tag, text: str, convert_as_inline: bool = False
    ) -> str:
        if el.img:
            link = el.img.get("src")
            caption = "Figure"
            if el.figcaption:
                caption = el.figcaption.text
            return f"\n\n![{caption}]({self.base_url}/{link})\n\n"
        elif el.table:
            caption = "Table"
            if el.figcaption:
                caption = el.figcaption.text
            table_text = self.process_tag(el.table, convert_as_inline=False)
            return f"\n\n{caption}\n\n{table_text}\n\n"
        return text


def _get_md_from_html(paper_id: str) -> str:
    url = f"https://arxiv.org/html/{paper_id}"
    response = requests.get(url)
    response.raise_for_status()
    content = response.text

    soup = bs4.BeautifulSoup(content, features="lxml")
    article = soup.article
    converter = ArxivHTMLConverter(
        base_url=url, strip=["section", "div", "a"], heading_style="ATX"
    )

    md_content: str = converter.convert_soup(article)
    md_content = md_content.replace("\xa0", " ")
    md_content = "\n".join([line.strip() for line in md_content.split("\n")])
    lines = [line.strip() for line in md_content.split("\n\n") if line.strip()]
    md_content = "\n\n".join(lines)
    return md_content


def _get_text_from_pdf(paper_id: str) -> str:
    url = f"https://arxiv.org/pdf/{paper_id}"
    pdf_path: Path = WORKSPACE_DIR_PATH / (paper_id + ".pdf")
    if not pdf_path.exists():
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type")
        assert content_type
        assert "application/pdf" in content_type.lower()
        with open(pdf_path.resolve(), "wb") as fp:
            fp.write(response.content)

    # Why not Marker? Because it is too heavy.
    reader = PdfReader(str(pdf_path.resolve()))

    full_text = ""
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
        except Exception:
            continue
        full_text += f"==== Page {page_number} ====\n{text}\n"
    return full_text


def arxiv_download(paper_id: str) -> str:
    """
    Downloads a paper from Arxiv and converts it to Markdown.

    Returns a Markdown version of the paper.
    Also saves it to the work directory as {paper_id}.md.

    Args:
        paper_id: ID of the paper on Arxiv. For instance: 2409.06820v1
    """

    try:
        content = _get_md_from_html(paper_id)
    except requests.exceptions.HTTPError:
        content = _get_text_from_pdf(paper_id)

    md_output_filename = WORKSPACE_DIR_PATH / f"{paper_id}.md"
    md_output_filename.write_text(content)
    return content
