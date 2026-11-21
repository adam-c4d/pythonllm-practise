"""Settings: where things live. Each one can be changed with an environment variable."""

import os
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    """Walk up from this file until we find the folder that holds 03_ml/."""
    for folder in [start, *start.parents]:
        if (folder / "03_ml").is_dir():
            return folder
    raise FileNotFoundError("Can't find the repo root (the folder with 03_ml/).")


REPO_ROOT = find_repo_root(Path(__file__).resolve().parent)
DEFAULT_MODEL = REPO_ROOT / "03_ml" / "models" / "diamond_price_model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL))
