from pathlib import Path


def find_project_root() -> Path:
    """Find project root by looking for pyproject.toml"""
    current = Path(__file__).parent
    for parent in [current] + list(current.parents):
        if (parent / 'pyproject.toml').exists():
            return parent
        if (parent / 'requirements.txt').exists():
            return parent
    raise FileNotFoundError("Could not find project root")