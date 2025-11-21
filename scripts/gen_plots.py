#!/usr/bin/env python3
"""Generate simple SVG plots from cpu_tb textual traces."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LOG_PATH = ASSETS / "cpu.log"

TRACE_RE = re.compile(
    r"TRACE cycle=(?P<cycle>\d+) pc=(?P<pc>\d+) opcode=(?P<opcode>[0-9a-fA-F]+) "
    r"alu=(?P<alu>-?\d+) acc=(?P<acc>-?\d+) rs1=(?P<rs1>-?\d+) rs2=(?P<rs2>-?\d+)"
)

OPCODE_NAMES = {
    0x0: "ADD",
    0x1: "SUB",
    0x2: "AND",
    0x3: "OR",
    0x4: "XOR",
    0x5: "LOADI",
    0x6: "LOADHI",
    0x8: "MAC4",
    0xD: "CONV3",
    0xE: "SIGMOID",
    0xF: "ACC",
}

OPCODE_COLORS = {
    0x0: "#1f77b4",
    0x5: "#ff7f0e",
    0x6: "#2ca02c",
    0x8: "#d62728",
    0xD: "#9467bd",
    0xE: "#8c564b",
    0xF: "#e377c2",
}

FEATURE_EVENTS = {
    0x8: "MAC4",
    0xD: "CONV3",
    0xE: "SIG",
    0xF: "ACC",
}


def parse_trace(path: Path):
    if not path.exists():
        raise SystemExit(f"Trace log not found: {path}")

    entries = []
    with path.open() as fh:
        for line in fh:
            match = TRACE_RE.search(line)
            if match:
                entry = {k: int(v, 16) if k == "opcode" else int(v) for k, v in match.groupdict().items()}
                entries.append(entry)
    if not entries:
        raise SystemExit("No TRACE lines found in log. Re-run the simulation to populate cpu.log.")
    return entries


def normalize(values):
    vmin = min(values)
    vmax = max(values)
    if vmax == vmin:
        vmax += 1
        vmin -= 1
    return vmin, vmax


def polyline_points(cycles, values, width, height, margin, y_offset):
    x0 = cycles[0]
    span_x = max(1, cycles[-1] - x0)
    vmin, vmax = normalize(values)
    span_y = vmax - vmin
    scale_x = (width - 2 * margin) / span_x
    scale_y = (height - 2 * margin) / span_y
    pts = []
    for cycle, value in zip(cycles, values):
        x = margin + (cycle - x0) * scale_x
        y = y_offset + height - margin - (value - vmin) * scale_y
        pts.append(f"{x:.2f},{y:.2f}")
    return pts, vmin, vmax


def build_waveform_svg(data):
    cycles = [entry["cycle"] for entry in data]
    series = [
        ("Program Counter", [entry["pc"] for entry in data], "#1f77b4"),
        ("ALU Result", [entry["alu"] for entry in data], "#ff7f0e"),
        ("Accumulator", [entry["acc"] for entry in data], "#2ca02c"),
    ]
    panel_height = 220
    width = 1100
    margin = 60
    total_height = panel_height * len(series)
    layers = []

    for idx, (label, values, color) in enumerate(series):
        y_off = idx * panel_height
        pts, vmin, vmax = polyline_points(cycles, values, width, panel_height, margin, y_off)
        grid_lines = []
        for frac in [0.25, 0.5, 0.75]:
            y = y_off + margin + (panel_height - 2 * margin) * frac
            grid_lines.append(
                f"<line x1=\"{margin}\" y1=\"{y:.2f}\" x2=\"{width - margin}\" y2=\"{y:.2f}\" stroke=\"#e5e5e5\" stroke-dasharray=\"4 4\"/>"
            )

        event_tags = []
        for entry in data:
            opcode = entry["opcode"]
            if opcode in FEATURE_EVENTS:
                x = margin + (entry["cycle"] - cycles[0]) * (width - 2 * margin) / max(1, cycles[-1] - cycles[0])
                event_tags.append(
                    f"<line x1=\"{x:.2f}\" y1=\"{y_off + margin}\" x2=\"{x:.2f}\" y2=\"{y_off + panel_height - margin}\" stroke=\"#bbbbbb\" stroke-dasharray=\"3 4\"/>"
                )
                event_tags.append(
                    f"<text x=\"{x:.2f}\" y=\"{y_off + margin - 10}\" font-size=\"12\" text-anchor=\"middle\" fill=\"#666\">{FEATURE_EVENTS[opcode]}</text>"
                )

        layers.append(
            f"<g>\n"
            f"  <rect x=\"{margin}\" y=\"{y_off + margin}\" width=\"{width - 2 * margin}\" height=\"{panel_height - 2 * margin}\" fill=\"#fafafa\" stroke=\"#cccccc\" stroke-width=\"1\"/>\n"
            f"  {''.join(grid_lines)}\n"
            f"  {''.join(event_tags)}\n"
            f"  <polyline fill=\"none\" stroke=\"{color}\" stroke-width=\"3\" points=\"{' '.join(pts)}\"/>\n"
            f"  <text x=\"{margin}\" y=\"{y_off + 25}\" font-size=\"18\" fill=\"#333\">{label} (range {vmin}..{vmax})</text>\n"
            f"</g>"
        )

    svg = (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{total_height}\" viewBox=\"0 0 {width} {total_height}\">\n"
        + "\n".join(layers)
        + "\n</svg>\n"
    )
    out_path = ASSETS / "sim_waveforms.svg"
    out_path.write_text(svg)
    return out_path


def build_accumulator_svg(data):
    cycles = [entry["cycle"] for entry in data]
    accs = [entry["acc"] for entry in data]
    width = 1100
    height = 360
    margin = 70
    pts, vmin, vmax = polyline_points(cycles, accs, width, height, margin, 0)
    circles = []
    labels = []
    for entry, point in zip(data, pts):
        x, y = point.split(",")
        if entry["opcode"] == 0xF:
            circles.append(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"6\" fill=\"#2ca02c\" stroke=\"#ffffff\" stroke-width=\"2\"/>")
            labels.append(f"<text x=\"{x}\" y=\"{float(y) - 12:.2f}\" font-size=\"12\" text-anchor=\"middle\" fill=\"#2e6b2e\">+={entry['rs1']}</text>")
        else:
            circles.append(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"3\" fill=\"#8ad18a\"/>")
    svg = (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">\n"
        f"  <rect x=\"{margin}\" y=\"{margin}\" width=\"{width - 2 * margin}\" height=\"{height - 2 * margin}\" fill=\"#fafafa\" stroke=\"#cccccc\"/>\n"
        f"  <polyline fill=\"none\" stroke=\"#2ca02c\" stroke-width=\"4\" points=\"{' '.join(pts)}\"/>\n"
        f"  {''.join(circles)}\n"
        f"  {''.join(labels)}\n"
        f"  <text x=\"{margin}\" y=\"45\" font-size=\"20\">Accumulator Evolution (final {accs[-1]})</text>\n"
        f"</svg>\n"
    )
    out_path = ASSETS / "accumulator.svg"
    out_path.write_text(svg)
    return out_path


def build_opcode_timeline_svg(data):
    cycles = [entry["cycle"] for entry in data]
    opcodes = [entry["opcode"] for entry in data]
    width = 1100
    height = 260
    margin = 60
    x0 = cycles[0]
    span = max(1, cycles[-1] - x0)
    scale_x = (width - 2 * margin) / span
    chart_height = height - 2 * margin

    blocks = []
    annotations = []
    for idx, (cycle, opcode) in enumerate(zip(cycles, opcodes)):
        next_cycle = cycles[idx + 1] if idx + 1 < len(cycles) else cycle + 1
        x = margin + (cycle - x0) * scale_x
        block_width = max(1, (next_cycle - cycle) * scale_x)
        color = OPCODE_COLORS.get(opcode, "#7f7f7f")
        blocks.append(
            f"<rect x=\"{x:.2f}\" y=\"{margin}\" width=\"{block_width:.2f}\" height=\"{chart_height}\" fill=\"{color}\" opacity=\"0.4\" stroke=\"#444\" stroke-width=\"0.5\"/>"
        )
        annotations.append(
            f"<text x=\"{x + block_width / 2:.2f}\" y=\"{margin + chart_height / 2:.2f}\" font-size=\"14\" text-anchor=\"middle\" fill=\"#111\">{OPCODE_NAMES.get(opcode, hex(opcode))}</text>"
        )

    ticks = []
    for entry in data:
        x = margin + (entry["cycle"] - x0) * scale_x
        ticks.append(f"<line x1=\"{x:.2f}\" y1=\"{margin + chart_height}\" x2=\"{x:.2f}\" y2=\"{margin + chart_height + 8}\" stroke=\"#999\"/>")
        ticks.append(f"<text x=\"{x:.2f}\" y=\"{height - 5}\" font-size=\"10\" text-anchor=\"middle\">{entry['cycle']}</text>")

    legend_elements = []
    legend_x = margin
    legend_y = 25
    for opcode, color in OPCODE_COLORS.items():
        legend_elements.append(
            f"<rect x=\"{legend_x}\" y=\"{legend_y}\" width=\"22\" height=\"12\" fill=\"{color}\" opacity=\"0.6\" stroke=\"#444\" stroke-width=\"0.5\"/>"
        )
        legend_elements.append(
            f"<text x=\"{legend_x + 28}\" y=\"{legend_y + 11}\" font-size=\"12\">{OPCODE_NAMES.get(opcode, hex(opcode))}</text>"
        )
        legend_x += 110

    svg = (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">\n"
        f"  <rect x=\"{margin}\" y=\"{margin}\" width=\"{width - 2 * margin}\" height=\"{chart_height}\" fill=\"#fafafa\" stroke=\"#cccccc\"/>\n"
        f"  {''.join(blocks)}\n"
        f"  {''.join(annotations)}\n"
        f"  {''.join(ticks)}\n"
        f"  {''.join(legend_elements)}\n"
        f"  <text x=\"{width / 2}\" y=\"{margin - 18}\" font-size=\"20\" text-anchor=\"middle\">Opcode Timeline</text>\n"
        f"</svg>\n"
    )
    out_path = ASSETS / "opcode_timeline.svg"
    out_path.write_text(svg)
    return out_path


def main():
    ASSETS.mkdir(exist_ok=True)
    entries = parse_trace(LOG_PATH)
    outputs = [
        build_waveform_svg(entries),
        build_accumulator_svg(entries),
        build_opcode_timeline_svg(entries),
    ]
    print("Generated SVG plots:")
    for path in outputs:
        print(f" - {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
