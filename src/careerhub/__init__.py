"""CareerHubZero central operations package."""

from pathlib import Path


def _version() -> str:
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return "0+unknown"


__version__ = _version()
