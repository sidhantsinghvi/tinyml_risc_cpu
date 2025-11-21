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
    panel_height = 180
    width = 900
    margin = 40
    total_height = panel_height * len(series)
    layers = []

    for idx, (label, values, color) in enumerate(series):
        y_off = idx * panel_height
        pts, vmin, vmax = polyline_points(cycles, values, width, panel_height, margin, y_off)
        layers.append(
            f"<g>\n"
            f"  <rect x=\"{margin}\" y=\"{y_off + margin}\" width=\"{width - 2 * margin}\" height=\"{panel_height - 2 * margin}\" fill=\"none\" stroke=\"#cccccc\" stroke-width=\"1\"/>\n"
            f"  <polyline fill=\"none\" stroke=\"{color}\" stroke-width=\"2\" points=\"{' '.join(pts)}\"/>\n"
            f"  <text x=\"{margin}\" y=\"{y_off + 20}\" font-size=\"16\" fill=\"#333\">{label} (range {vmin}..{vmax})</text>\n"
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
    width = 900
    height = 300
    margin = 50
    pts, vmin, vmax = polyline_points(cycles, accs, width, height, margin, 0)
    circles = []
    for point in pts:
        x, y = point.split(",")
        circles.append(f"<circle cx=\"{x}\" cy=\"{y}\" r=\"4\" fill=\"#2ca02c\"/>")
    svg = (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">\n"
        f"  <rect x=\"{margin}\" y=\"{margin}\" width=\"{width - 2 * margin}\" height=\"{height - 2 * margin}\" fill=\"none\" stroke=\"#cccccc\"/>\n"
        f"  <polyline fill=\"none\" stroke=\"#2ca02c\" stroke-width=\"2\" points=\"{' '.join(pts)}\"/>\n"
        f"  {''.join(circles)}\n"
        f"  <text x=\"{margin}\" y=\"30\" font-size=\"18\">Accumulator Evolution (final {accs[-1]})</text>\n"
        f"</svg>\n"
    )
    out_path = ASSETS / "accumulator.svg"
    out_path.write_text(svg)
    return out_path


def build_opcode_timeline_svg(data):
    cycles = [entry["cycle"] for entry in data]
    opcodes = [entry["opcode"] for entry in data]
    width = 900
    height = 220
    margin = 40
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

    svg = (
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">\n"
        f"  <rect x=\"{margin}\" y=\"{margin}\" width=\"{width - 2 * margin}\" height=\"{chart_height}\" fill=\"none\" stroke=\"#cccccc\"/>\n"
        f"  {''.join(blocks)}\n"
        f"  {''.join(annotations)}\n"
        f"  <text x=\"{width / 2}\" y=\"{height - 10}\" font-size=\"16\" text-anchor=\"middle\">Opcode Timeline</text>\n"
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
