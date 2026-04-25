"""Run drift-correction processing from the scripts entry point."""

from __future__ import annotations

import sys
from pathlib import Path


def _project_root() -> Path:
    """Return the absolute path of the project root based on this file location."""
    return Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    project_root = _project_root()

    # Ensure imports from the project root (e.g., src.drift_correction.*) are available.
    sys.path.insert(0, str(project_root))

    from src.drift_correction.processor import process_drift_data

    data_dir = project_root / "data"
    output_dir = project_root / "output"

    input_file = data_dir / "Drift Profile for ABFGrabber1.txt"
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    process_drift_data(
        filepath=str(input_file),
        output_dir=str(output_dir),
        filename="Drift Profile for ABFGrabber1_corrected.txt",
    )
