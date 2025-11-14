#!/usr/bin/env python3
"""Generate SVG bar charts with local vs cloud color coding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


OUTPUT_DIR = Path("docs/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PALETTE = {
    "local": "#2E7D32",
    "cloud": "#1976D2",
}


@dataclass(frozen=True)
class Bar:
    label: str
    value: float
    category: str  # "local" or "cloud"


def svg_header(width: int, height: int) -> list[str]:
    return [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\"",
        "     xmlns=\"http://www.w3.org/2000/svg\" role=\"img\">",
        '<style>text{font-family:\'Inter\',\'Segoe UI\',sans-serif;}</style>',
    ]


def add_legend(lines: list[str], margin: dict[str, int]) -> None:
    legend_x = margin["left"]
    legend_y = margin["top"] - 30
    offset = 0
    for label, color in ("Local", PALETTE["local"]), ("Cloud", PALETTE["cloud"]):
        x = legend_x + offset
        lines.append(
            f"  <rect x=\"{x}\" y=\"{legend_y}\" width=\"18\" height=\"18\" rx=\"3\" fill=\"{color}\" />"
        )
        lines.append(
            f"  <text x=\"{x + 24}\" y=\"{legend_y + 14}\" font-size=\"16\" fill=\"#222\">{label}</text>"
        )
        offset += 120


def build_chart(
    filename: str,
    title: str,
    bars: list[Bar],
    x_label: str,
    x_min: float,
    x_max: float,
    ticks: list[float],
    value_suffix: str = "%",
) -> None:
    width = 1000
    margin = {"left": 180, "right": 60, "top": 80, "bottom": 80}
    bar_height = 32
    gap = 18
    chart_height = len(bars) * (bar_height + gap) - gap
    height = margin["top"] + chart_height + margin["bottom"]
    x_scale = (width - margin["left"] - margin["right"]) / (x_max - x_min)

    lines = svg_header(width, height)
    lines.append(f"  <rect width=\"{width}\" height=\"{height}\" fill=\"#fff\" />")
    lines.append(
        f"  <text x=\"{width/2}\" y=\"40\" font-size=\"28\" text-anchor=\"middle\" fill=\"#111\">{title}</text>"
    )

    add_legend(lines, margin)

    axis_y = height - margin["bottom"]
    lines.append(
        f"  <line x1=\"{margin['left']}\" y1=\"{axis_y}\" x2=\"{width - margin['right']}\" y2=\"{axis_y}\" stroke=\"#ccc\" stroke-width=\"2\" />"
    )

    for tick in ticks:
        x = margin["left"] + (tick - x_min) * x_scale
        lines.append(
            f"  <line x1=\"{x}\" y1=\"{axis_y}\" x2=\"{x}\" y2=\"{axis_y + 8}\" stroke=\"#999\" stroke-width=\"2\" />"
        )
        lines.append(
            f"  <text x=\"{x}\" y=\"{axis_y + 28}\" font-size=\"16\" text-anchor=\"middle\" fill=\"#444\">{tick:g}{value_suffix}</text>"
        )

    text_x = margin["left"] - 20
    current_y = margin["top"]
    for bar in bars:
        bar_width = (bar.value - x_min) * x_scale
        color = PALETTE[bar.category]
        lines.append(
            f"  <rect x=\"{margin['left']}\" y=\"{current_y}\" width=\"{bar_width}\" height=\"{bar_height}\" rx=\"5\" fill=\"{color}\" />"
        )
        lines.append(
            f"  <text x=\"{text_x}\" y=\"{current_y + bar_height / 2 + 5}\" font-size=\"18\" text-anchor=\"end\" fill=\"#111\">{bar.label}</text>"
        )
        lines.append(
            f"  <text x=\"{margin['left'] + bar_width + 12}\" y=\"{current_y + bar_height / 2 + 6}\" font-size=\"18\" fill=\"#111\">{bar.value:.2f}{value_suffix}</text>"
        )
        current_y += bar_height + gap

    lines.append(
        f"  <text x=\"{width/2}\" y=\"{height - 20}\" font-size=\"18\" text-anchor=\"middle\" fill=\"#333\">{x_label}</text>"
    )
    lines.append("</svg>")

    (OUTPUT_DIR / filename).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    build_chart(
        filename="word_accuracy.svg",
        title="Word Accuracy Comparison",
        bars=[
            Bar("Whisper-Base", 82.48, "local"),
            Bar("Whisper-Base*", 82.48, "local"),
            Bar("Deepgram Nova-3", 81.28, "cloud"),
            Bar("AssemblyAI", 81.21, "cloud"),
            Bar("OpenAI Whisper-1", 80.73, "cloud"),
            Bar("Gladia Solaria-1", 79.17, "cloud"),
            Bar("Speechmatics SLAM-1", 78.35, "cloud"),
            Bar("Whisper-Tiny", 77.51, "local"),
        ],
        x_label="Word Accuracy (%)",
        x_min=75,
        x_max=85,
        ticks=[75, 77.5, 80, 82.5, 85],
    )

    build_chart(
        filename="punctuation_accuracy.svg",
        title="Punctuation Accuracy Comparison",
        bars=[
            Bar("Deepgram Nova-3", 51.17, "cloud"),
            Bar("AssemblyAI", 48.43, "cloud"),
            Bar("OpenAI Whisper-1", 44.44, "cloud"),
            Bar("Gladia Solaria-1", 44.13, "cloud"),
            Bar("Speechmatics SLAM-1", 38.23, "cloud"),
            Bar("Whisper-Base", 21.90, "local"),
            Bar("Whisper-Tiny", 18.78, "local"),
        ],
        x_label="Punctuation Accuracy (%)",
        x_min=0,
        x_max=55,
        ticks=[0, 10, 20, 30, 40, 50],
    )

    build_chart(
        filename="wer.svg",
        title="Word Error Rate (Lower is Better)",
        bars=[
            Bar("Whisper-Base", 17.52, "local"),
            Bar("Whisper-Base*", 17.52, "local"),
            Bar("Deepgram Nova-3", 18.72, "cloud"),
            Bar("AssemblyAI", 18.79, "cloud"),
            Bar("OpenAI Whisper-1", 19.27, "cloud"),
            Bar("Gladia Solaria-1", 20.83, "cloud"),
            Bar("Speechmatics SLAM-1", 21.65, "cloud"),
            Bar("Whisper-Tiny", 22.49, "local"),
        ],
        x_label="Word Error Rate (%)",
        x_min=15,
        x_max=25,
        ticks=[15, 17, 19, 21, 23, 25],
    )

    build_chart(
        filename="local_vs_cloud.svg",
        title="Local vs Cloud: Word Accuracy & Punctuation",
        bars=[
            Bar("Local Avg Word", 80.82, "local"),
            Bar("Cloud Avg Word", 80.10, "cloud"),
            Bar("Local Avg Punctuation", 20.86, "local"),
            Bar("Cloud Avg Punctuation", 45.28, "cloud"),
        ],
        x_label="Accuracy (%)",
        x_min=0,
        x_max=85,
        ticks=[0, 20, 40, 60, 80],
    )


if __name__ == "__main__":
    main()
