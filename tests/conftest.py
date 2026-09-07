from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def work_root() -> Path:
    # Single SoT (Option B): the engine tree owns fixtures, adapters, honesty.
    return ROOT / "engine"

@pytest.fixture
def schemas_dir(work_root: Path) -> Path:
    return work_root / "schemas"
