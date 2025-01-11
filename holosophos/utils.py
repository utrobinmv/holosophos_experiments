from typing import Any
from pathlib import Path

from jinja2 import Template


DIR_PATH = Path(__file__).parent
PROMPTS_DIR_PATH = DIR_PATH / "prompts"


def get_prompt(template_name: str) -> str:
    template_path = PROMPTS_DIR_PATH / f"{template_name}.jinja"
    with open(template_path) as f:
        template = f.read()
    return template


def encode_prompt(template_name: str, **kwargs: Any) -> str:
    text = get_prompt(template_name)
    template = Template(text)
    return template.render(**kwargs).strip() + "\n"
