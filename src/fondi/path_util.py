from __future__ import annotations

import re


def _parse_path_numbers(d: str) -> list[tuple[float, float]]:
    """Extract (x, y) pairs from M/L/C commands in fondi path data."""
    points: list[tuple[float, float]] = []
    tokens = re.findall(r"[MLCZ]|-?\d*\.?\d+(?:e[-+]?\d+)?", d, re.I)
    i = 0
    cmd = "M"
    while i < len(tokens):
        tok = tokens[i]
        if tok.upper() in "MLCZ":
            cmd = tok.upper()
            i += 1
            if cmd == "Z":
                continue
            continue
        nums = []
        while i < len(tokens) and tokens[i].upper() not in "MLCZ":
            nums.append(float(tokens[i]))
            i += 1
        if cmd == "M" or cmd == "L":
            for j in range(0, len(nums) - 1, 2):
                points.append((nums[j], nums[j + 1]))
        elif cmd == "C":
            for j in range(0, len(nums) - 5, 6):
                points.append((nums[j], nums[j + 1]))
                points.append((nums[j + 2], nums[j + 3]))
                points.append((nums[j + 4], nums[j + 5]))
    return points


def path_bounds(d: str, stroke_width: float) -> tuple[float, float, float, float]:
    points = _parse_path_numbers(d)
    if not points:
        return 0.0, 0.0, 0.0, 0.0
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    pad = stroke_width / 2
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def _cubic_bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    n: int,
) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = (
            u**3 * p0[0]
            + 3 * u**2 * t * p1[0]
            + 3 * u * t**2 * p2[0]
            + t**3 * p3[0]
        )
        y = (
            u**3 * p0[1]
            + 3 * u**2 * t * p1[1]
            + 3 * u * t**2 * p2[1]
            + t**3 * p3[1]
        )
        out.append((x, y))
    return out


def sample_path_subpaths(d: str, n_per_curve: int = 32) -> list[list[tuple[float, float]]]:
    """Sample fondi path to one polyline per subpath (split on M)."""
    tokens = re.findall(r"[MLCZ]|-?\d*\.?\d+(?:e[-+]?\d+)?", d, re.I)
    subpaths: list[list[tuple[float, float]]] = []
    points: list[tuple[float, float]] = []
    i = 0
    cmd = "M"
    current = (0.0, 0.0)
    while i < len(tokens):
        tok = tokens[i]
        if tok.upper() in "MLCZ":
            cmd = tok.upper()
            i += 1
            if cmd == "Z":
                if points:
                    points.append(points[0])
                continue
            if cmd == "M" and points:
                subpaths.append(points)
                points = []
            continue
        nums = []
        while i < len(tokens) and tokens[i].upper() not in "MLCZ":
            nums.append(float(tokens[i]))
            i += 1
        if cmd == "M":
            for j in range(0, len(nums) - 1, 2):
                current = (nums[j], nums[j + 1])
                points.append(current)
        elif cmd == "L":
            for j in range(0, len(nums) - 1, 2):
                current = (nums[j], nums[j + 1])
                points.append(current)
        elif cmd == "C":
            for j in range(0, len(nums) - 5, 6):
                p0 = current
                p1 = (nums[j], nums[j + 1])
                p2 = (nums[j + 2], nums[j + 3])
                p3 = (nums[j + 4], nums[j + 5])
                segment = _cubic_bezier(p0, p1, p2, p3, n_per_curve)
                if points and segment:
                    segment = segment[1:]
                points.extend(segment)
                current = p3
    if points:
        subpaths.append(points)
    return subpaths


def sample_path_d(d: str, n_per_curve: int = 24) -> list[tuple[float, float]]:
    """Sample fondi path to polyline points (all subpaths concatenated)."""
    out: list[tuple[float, float]] = []
    for sub in sample_path_subpaths(d, n_per_curve):
        out.extend(sub)
    return out


def fondi_path_to_svg_d(d: str, scene_height: float) -> str:
    """Flip y coordinates in path data for SVG output."""

    def flip_y(y: float) -> float:
        return scene_height - y

    tokens = re.findall(r"[MLCZ]|-?\d*\.?\d+(?:e[-+]?\d+)?", d, re.I)
    out: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.upper() in "MLCZ":
            out.append(tok.upper())
            i += 1
            continue
        nums = []
        while i < len(tokens) and tokens[i].upper() not in "MLCZ":
            nums.append(float(tokens[i]))
            i += 1
        cmd = out[-1] if out else "M"
        if cmd == "C":
            for j in range(0, len(nums) - 5, 6):
                out.extend(
                    [
                        str(round(nums[j], 3)),
                        str(round(flip_y(nums[j + 1]), 3)),
                        str(round(nums[j + 2], 3)),
                        str(round(flip_y(nums[j + 3]), 3)),
                        str(round(nums[j + 4], 3)),
                        str(round(flip_y(nums[j + 5]), 3)),
                    ]
                )
        else:
            for j in range(0, len(nums) - 1, 2):
                out.append(str(round(nums[j], 3)))
                out.append(str(round(flip_y(nums[j + 1]), 3)))
    return " ".join(out)
