from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def work_root() -> Path:
    return ROOT

@pytest.fixture
def schemas_dir(work_root: Path) -> Path:
    return work_root / "schemas"
