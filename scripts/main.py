"""Run drift-correction processing from the scripts entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


def _project_root() -> Path:
    """Return the absolute path of the project root based on this file location."""
    return Path(__file__).resolve().parents[1]


def _load_config(config_path: Path) -> dict[str, Any]:
    """Load YAML configuration file and return it as a dictionary."""
    with config_path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    if not isinstance(loaded, dict):
        raise ValueError(f"Invalid config format in: {config_path}")
    return loaded


def _generate_output_filename(input_filename: str) -> str:
    """Generate output filename by appending '_corrected' before the file extension.
    
    Examples:
        'data.txt' -> 'data_corrected.txt'
        'Drift Profile for Frame Grabber.txt' -> 'Drift Profile for Frame Grabber_corrected.txt'
    """
    input_path = Path(input_filename)
    stem = input_path.stem
    suffix = input_path.suffix
    return f"{stem}_corrected{suffix}"


if __name__ == "__main__":
    project_root = _project_root()

    # Ensure imports from the project root (e.g., src.drift_correction.*) are available.
    sys.path.insert(0, str(project_root))

    from src.drift_correction.processor import process_drift_data

    config = _load_config(project_root / "config.yaml")

    paths_cfg = config.get("paths", {})
    files_cfg = config.get("files", {})
    processing_cfg = config.get("processing", {})

    if not isinstance(paths_cfg, dict) or not isinstance(files_cfg, dict) or not isinstance(processing_cfg, dict):
        raise ValueError("Config sections 'paths', 'files', and 'processing' must be mappings.")

    data_dir = project_root / str(paths_cfg.get("input_dir", "data"))
    output_dir = project_root / str(paths_cfg.get("output_dir", "output"))

    input_name = str(files_cfg.get("input", "Drift Profile for ABFGrabber1.txt"))
    output_name = _generate_output_filename(input_name)

    input_file = data_dir / input_name
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    process_drift_data(
        filepath=str(input_file),
        output_dir=str(output_dir),
        filename=output_name,
        x_threshold=float(processing_cfg.get("x_threshold", 20.0)),
        y_threshold=float(processing_cfg.get("y_threshold", 10.0)),
        show_plot=bool(processing_cfg.get("show_plot", False)),
        x_color=str(processing_cfg.get("x_color", "blue")),
        y_color=str(processing_cfg.get("y_color", "red")),
    )
