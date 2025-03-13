import os
from pathlib import Path

DIR_PATH = Path(__file__).parent
ROOT_PATH = DIR_PATH.parent
WORKSPACE_DIR_PATH = ROOT_PATH / "workdir"
PROJECT_HOST_ROOT_PATH = Path(os.getenv("PROJECT_HOST_ROOT_PATH", ROOT_PATH))
WORKSPACE_DIR_HOST_PATH = PROJECT_HOST_ROOT_PATH / "workdir"
PROMPTS_DIR_PATH = DIR_PATH / "prompts"
