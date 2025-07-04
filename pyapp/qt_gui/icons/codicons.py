from pathlib import Path

from ...logging import log_func_call
from ..utils import load_icon

HERE = Path(__file__).parent
ICONS_DIR = HERE/"vscode-codicons/src/icons"


@log_func_call
def get_codicon(name: str):
    return load_icon(ICONS_DIR/f"{name}.svg")
