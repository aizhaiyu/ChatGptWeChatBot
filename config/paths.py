from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = DATA_DIR / "memory"
IMAGE_DIR = PROJECT_ROOT / "img"
LOG_DIR = PROJECT_ROOT / "logs"


def project_path(*parts):
    return PROJECT_ROOT.joinpath(*parts)
