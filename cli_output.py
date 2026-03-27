"""Terminal-friendly formatting helpers for the PawPal+ CLI demo."""

from __future__ import annotations

import os
import sys
from typing import Iterable, Sequence

try:
    from tabulate import tabulate
except ImportError:  # pragma: no cover - exercised only when dependency is missing.
    def tabulate(
        rows: Sequence[Sequence[object]],
        headers: Sequence[object],
        tablefmt: str = "simple",
    ) -> str:
        """Fallback table renderer when tabulate is unavailable."""
        del tablefmt
        string_rows = [[str(cell) for cell in row] for row in rows]
        string_headers = [str(header) for header in headers]
        widths = [
            max(len(string_headers[index]), *(len(row[index]) for row in string_rows))
            for index in range(len(string_headers))
        ]

        def build_line(values: Sequence[str]) -> str:
            return " | ".join(value.ljust(widths[index]) for index, value in enumerate(values))

        separator = "-+-".join("-" * width for width in widths)
        body = [build_line(row) for row in string_rows]
        return "\n".join([build_line(string_headers), separator, *body])


RESET = "\033[0m"
COLORS = {
    "red": "\033[91m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "bold": "\033[1m",
}

CATEGORY_EMOJIS = {
    "feeding": "🥣",
    "exercise": "🐾",
    "medication": "💊",
    "grooming": "✂️",
    "enrichment": "🧩",
    "other": "📌",
}


def supports_color() -> bool:
    """Return whether ANSI colors are likely to render correctly."""
    return sys.stdout.isatty() and os.getenv("TERM") not in {None, "", "dumb"}


def colorize(text: str, color: str, *, use_color: bool | None = None) -> str:
    """Wrap text in ANSI color codes when enabled."""
    enabled = supports_color() if use_color is None else use_color
    if not enabled:
        return text
    return f"{COLORS[color]}{text}{RESET}"


def emoji_for_category(category: str) -> str:
    """Return the icon used for a task category."""
    return CATEGORY_EMOJIS.get(category.lower(), CATEGORY_EMOJIS["other"])


def format_priority(priority: str, *, use_color: bool | None = None) -> str:
    """Render a readable priority label."""
    normalized = priority.lower()
    color = {"high": "red", "medium": "yellow", "low": "green"}.get(normalized, "blue")
    return colorize(normalized.upper(), color, use_color=use_color)


def format_status(completed: bool, *, use_color: bool | None = None) -> str:
    """Render a readable completion label."""
    if completed:
        return colorize("DONE", "green", use_color=use_color)
    return colorize("PENDING", "yellow", use_color=use_color)


def format_title(title: str, category: str) -> str:
    """Attach a category emoji to a task title."""
    return f"{emoji_for_category(category)} {title}"


def format_section_heading(title: str, *, icon: str | None = None, use_color: bool | None = None) -> str:
    """Build a bold section heading for terminal output."""
    prefix = f"{icon} " if icon else ""
    heading = f"{prefix}{title}"
    return colorize(heading, "bold", use_color=use_color)


def render_kv_summary(items: Iterable[tuple[str, object]], *, use_color: bool | None = None) -> str:
    """Render a short list of labeled summary lines."""
    lines = [
        f"{colorize(label + ':', 'cyan', use_color=use_color)} {value}"
        for label, value in items
    ]
    return "\n".join(lines)


def render_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[object]],
    *,
    use_color: bool | None = None,
) -> str:
    """Render a consistent table format for CLI output."""
    del use_color
    if not rows:
        return "No items to show."
    return tabulate(rows, headers=headers, tablefmt="fancy_grid")
