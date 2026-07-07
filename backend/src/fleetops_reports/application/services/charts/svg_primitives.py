"""Shared SVG rendering helpers.

SAD Traceability: pure-stdlib SVG primitives for SAD section 10.5 visualizations.
"""

from __future__ import annotations

from html import escape


def escape_text(value: str) -> str:
    return escape(value, quote=True)


def svg_open(width: int, height: int) -> str:
    return (
        f"<svg xmlns='http://www.w3.org/2000/svg' "
        f"width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"
    )


def svg_background(width: int, height: int, fill: str) -> str:
    return f"<rect width='{width}' height='{height}' fill='{fill}'/>"


def svg_title(x: int, y: int, text: str, color: str, size: int = 20) -> str:
    return (
        f"<text x='{x}' y='{y}' font-family='Arial' font-size='{size}' "
        f"fill='{color}' font-weight='bold'>{escape_text(text)}</text>"
    )


def svg_label(x: int, y: int, text: str, color: str, size: int = 12) -> str:
    return (
        f"<text x='{x}' y='{y}' font-family='Arial' font-size='{size}' "
        f"fill='{color}' text-anchor='middle'>{escape_text(text)}</text>"
    )


def svg_value_label(x: int, y: int, text: str, color: str, size: int = 11) -> str:
    return (
        f"<text x='{x}' y='{y}' font-family='Arial' font-size='{size}' "
        f"fill='{color}' text-anchor='middle'>{escape_text(text)}</text>"
    )


def svg_line(x1: int, y1: int, x2: int, y2: int, color: str, width: int = 1) -> str:
    return (
        f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' "
        f"stroke='{color}' stroke-width='{width}'/>"
    )


def svg_rect(x: int, y: int, width: int, height: int, fill: str) -> str:
    return f"<rect x='{x}' y='{y}' width='{width}' height='{height}' fill='{fill}'/>"


def render_vertical_bar_chart(
    *,
    title: str,
    series: list[tuple[str, float]],
    width: int = 800,
    height: int = 400,
    background: str = "#f7fafc",
    bar_color: str = "#3182ce",
    text_color: str = "#1a202c",
    axis_color: str = "#cbd5e0",
    value_suffix: str = "",
    max_value: float | None = None,
) -> str:
    if not series:
        return ""

    margin_left = 60
    margin_right = 40
    margin_top = 50
    margin_bottom = 80
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    baseline_y = margin_top + chart_height

    peak = max_value if max_value is not None else max(value for _, value in series)
    if peak <= 0:
        peak = 1.0

    bar_gap = 16
    bar_width = max(20, (chart_width - bar_gap * (len(series) + 1)) // len(series))

    parts = [
        svg_open(width, height),
        svg_background(width, height, background),
        svg_title(32, 32, title, text_color),
        svg_line(margin_left, baseline_y, width - margin_right, baseline_y, axis_color, 2),
    ]

    for index, (label, value) in enumerate(series):
        bar_height = int((value / peak) * chart_height)
        x = margin_left + bar_gap + index * (bar_width + bar_gap)
        y = baseline_y - bar_height
        parts.append(svg_rect(x, y, bar_width, bar_height, bar_color))
        parts.append(
            svg_value_label(
                x + bar_width // 2,
                y - 6,
                f"{value:.1f}{value_suffix}",
                text_color,
            )
        )
        parts.append(
            svg_label(
                x + bar_width // 2,
                baseline_y + 20,
                label,
                text_color,
            )
        )

    parts.append("</svg>")
    return "".join(parts)


def render_horizontal_bar_chart(
    *,
    title: str,
    series: list[tuple[str, float]],
    width: int = 800,
    height: int = 400,
    background: str = "#f7fafc",
    bar_color: str = "#3182ce",
    text_color: str = "#1a202c",
    axis_color: str = "#cbd5e0",
    value_suffix: str = "",
) -> str:
    if not series:
        return ""

    margin_left = 160
    margin_right = 40
    margin_top = 50
    margin_bottom = 40
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    peak = max(value for _, value in series)
    if peak <= 0:
        peak = 1.0

    bar_gap = 12
    bar_height = max(16, (chart_height - bar_gap * (len(series) + 1)) // len(series))

    parts = [
        svg_open(width, height),
        svg_background(width, height, background),
        svg_title(32, 32, title, text_color),
        svg_line(margin_left, margin_top, margin_left, height - margin_bottom, axis_color, 2),
        svg_line(
            margin_left,
            height - margin_bottom,
            width - margin_right,
            height - margin_bottom,
            axis_color,
            2,
        ),
    ]

    for index, (label, value) in enumerate(series):
        bar_width = int((value / peak) * chart_width)
        y = margin_top + bar_gap + index * (bar_height + bar_gap)
        parts.append(svg_rect(margin_left, y, bar_width, bar_height, bar_color))
        parts.append(
            svg_label(margin_left - 10, y + bar_height // 2 + 4, label, text_color, size=11)
        )
        parts.append(
            svg_value_label(
                margin_left + bar_width + 24,
                y + bar_height // 2 + 4,
                f"{value:.1f}{value_suffix}",
                text_color,
            )
        )

    parts.append("</svg>")
    return "".join(parts)


def render_grouped_bar_chart(
    *,
    title: str,
    categories: list[str],
    groups: list[tuple[str, list[float], str]],
    width: int = 800,
    height: int = 400,
    background: str = "#f7fafc",
    text_color: str = "#1a202c",
    axis_color: str = "#cbd5e0",
) -> str:
    if not categories or not groups:
        return ""

    margin_left = 60
    margin_right = 40
    margin_top = 70
    margin_bottom = 80
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    baseline_y = margin_top + chart_height

    all_values = [value for _, values, _ in groups for value in values]
    peak = max(all_values) if all_values else 1.0
    if peak <= 0:
        peak = 1.0

    group_count = len(groups)
    category_gap = 24
    category_width = max(
        40,
        (chart_width - category_gap * (len(categories) + 1)) // len(categories),
    )
    inner_bar_width = max(8, (category_width - 8) // group_count)

    parts = [
        svg_open(width, height),
        svg_background(width, height, background),
        svg_title(32, 32, title, text_color),
        svg_line(margin_left, baseline_y, width - margin_right, baseline_y, axis_color, 2),
    ]

    legend_x = margin_left
    for group_index, (group_label, _, color) in enumerate(groups):
        legend_y = 48 + group_index * 16
        parts.append(svg_rect(legend_x, legend_y - 10, 12, 12, color))
        parts.append(
            svg_label(legend_x + 20, legend_y, group_label, text_color, size=11)
        )

    for cat_index, category in enumerate(categories):
        category_x = margin_left + category_gap + cat_index * (category_width + category_gap)
        for group_index, (_, values, color) in enumerate(groups):
            value = values[cat_index]
            bar_height = int((value / peak) * chart_height)
            x = category_x + group_index * inner_bar_width
            y = baseline_y - bar_height
            parts.append(svg_rect(x, y, inner_bar_width - 2, bar_height, color))
            if value > 0:
                parts.append(
                    svg_value_label(
                        x + inner_bar_width // 2,
                        y - 4,
                        f"{value:.0f}",
                        text_color,
                        size=10,
                    )
                )
        parts.append(
            svg_label(
                category_x + category_width // 2,
                baseline_y + 20,
                category,
                text_color,
            )
        )

    parts.append("</svg>")
    return "".join(parts)
