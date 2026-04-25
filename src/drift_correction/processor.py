"""Drift profile processing utilities.

This module provides range detection, discontinuity correction, and
an end-to-end pipeline for drift profile text files.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from sklearn.linear_model import LinearRegression

FloatArray = npt.NDArray[np.float64]
RangeList = list[tuple[int, int]]


def detect_ranges(
    data: FloatArray,
    threshold: float = 50.0,
    show_plot: bool = True,
    color: str = "black",
) -> RangeList:
    """Detect contiguous ranges separated by large jumps.

    Args:
        data: 1D drift signal.
        threshold: Absolute difference threshold used as a boundary.
        show_plot: If True, show the data with detected boundaries.
        color: Line color for plotting.

    Returns:
        List of (start, end) index pairs where end is exclusive.
    """
    ranges: RangeList = []
    start_idx = 0

    for i in range(len(data) - 1):
        if abs(data[i + 1] - data[i]) > threshold:
            ranges.append((start_idx, i + 1))
            start_idx = i + 1

    ranges.append((start_idx, len(data)))

    if show_plot:
        x_vals = np.arange(len(data), dtype=np.int64)
        plt.figure(figsize=(10, 5))
        plt.plot(x_vals, data, label="Original Data", linestyle="-", color=color)
        for i, (start, end) in enumerate(ranges):
            plt.axvline(
                x=start,
                color="green",
                linestyle="--",
                label="Range Start" if i == 0 else "",
            )
            plt.axvline(x=end - 1, color="green", linestyle="--")
        plt.title("Original Data with Auto-Detected Ranges")
        plt.xlabel("Index")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.show()

    return ranges


def correct_discontinuity(
    data: FloatArray,
    ranges: RangeList,
    show_plot: bool = True,
    color: str = "black",
) -> FloatArray:
    """Correct range-to-range discontinuities using linear extrapolation.

    Args:
        data: 1D drift signal before correction.
        ranges: Output ranges from detect_ranges.
        show_plot: If True, show corrected data with range boundaries.
        color: Line color for plotting.

    Returns:
        Corrected 1D drift signal.
    """
    corrected_data = data.copy()
    x_vals = np.arange(len(data), dtype=np.int64)

    for i in range(1, len(ranges)):
        start, end = ranges[i]
        ref_index = i - 1

        while ref_index >= 0 and (ranges[ref_index][1] - ranges[ref_index][0]) <= 1:
            ref_index -= 1
        if ref_index < 0:
            continue

        prev_start, prev_end = ranges[ref_index]
        x_range = x_vals[prev_start:prev_end].reshape(-1, 1)
        y_range = corrected_data[prev_start:prev_end]

        model = LinearRegression()
        model.fit(x_range, y_range)
        prev_slope = float(model.coef_[0])
        prev_intercept = float(model.intercept_)

        expected_y = prev_slope * float(start) + prev_intercept
        shift = corrected_data[start] - expected_y

        corrected_data[start:end] -= shift

    if show_plot:
        plt.figure(figsize=(12, 5))
        plt.plot(x_vals, corrected_data, label="Corrected Data", color=color)

        for i, (start, end) in enumerate(ranges):
            plt.axvline(
                x=start,
                color="green",
                linestyle="--",
                label="Range Start" if i == 0 else "",
            )
            plt.axvline(x=end - 1, color="green", linestyle="--")

        plt.xlabel("Index")
        plt.ylabel("Value")
        plt.title("Corrected Data with Range Boundaries")
        plt.grid(True)
        plt.legend()
        plt.show()

    return corrected_data


def process_drift_data(
    filepath: str,
    output_dir: str,
    filename: str,
    x_threshold: float = 20.0,
    y_threshold: float = 10.0,
    show_plot: bool = False,
    x_color: str = "blue",
    y_color: str = "red",
) -> None:
    """Run drift correction pipeline for X/Y drift and save the result.

    Args:
        filepath: Path to input text file loaded via np.loadtxt.
        output_dir: Directory for saving corrected output.
        filename: Output filename.
        x_threshold: Range detection threshold for X drift.
        y_threshold: Range detection threshold for Y drift.
        show_plot: If True, show plots during processing.
        x_color: Plot color for X drift.
        y_color: Plot color for Y drift.

    Returns:
        None.
    """
    raw = np.loadtxt(filepath)
    data = np.asarray(raw, dtype=np.float64)

    if data.ndim != 2 or data.shape[0] < 2:
        raise ValueError("Input file must contain at least two rows for X and Y drift.")

    x_drift: FloatArray = np.asarray(data[0], dtype=np.float64)
    y_drift: FloatArray = np.asarray(data[1], dtype=np.float64)

    x_ranges = detect_ranges(x_drift, threshold=x_threshold, show_plot=show_plot, color=x_color)
    x_corrected = correct_discontinuity(x_drift, x_ranges, show_plot=show_plot, color=x_color)

    y_ranges = detect_ranges(y_drift, threshold=y_threshold, show_plot=show_plot, color=y_color)
    y_corrected = correct_discontinuity(y_drift, y_ranges, show_plot=show_plot, color=y_color)

    indices: npt.NDArray[np.int64] = np.arange(1, len(x_corrected) + 1, dtype=np.int64)
    combined = np.column_stack((indices, x_corrected, y_corrected))

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    save_path = output_path / filename

    np.savetxt(
        save_path,
        combined,
        fmt="%d\t%.1f\t%.1f",
        header="Index\tx_corrected\ty_corrected",
        comments="",
    )
