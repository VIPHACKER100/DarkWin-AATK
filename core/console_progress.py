"""
DARKWIN — CLI / Console Progress Renderer
Reusable live 0-100% progress bar bound to ``core.progress``.

Used by both the ``darkwin run`` command and the dashboard backend console so
that every place a pipeline executes can show realtime progress:

- Interactive terminals: a live rich bar (phase label, bar, percent).
- Piped/non-TTY output: one clean ``[NN%] <message>`` line per update.

The pipeline modules only know about ``core.progress``; this module is a thin
view over it, so nothing below core needs to know how progress is displayed.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import Iterator

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn

from core import progress as progress_hub


def _make_console(*, file=None) -> Console:
    return Console(file=file or sys.stdout)


def _emit_plain(pct: int, message: str) -> None:
    """Fallback renderer for pipes where a live bar would interleave badly."""
    label = message or "working"
    print(f"[{pct:>3}%] {label}", flush=True)


@contextmanager
def cli_progress(description: str = "Scanning") -> Iterator[None]:
    """
    Context manager that shows a realtime progress bar while a pipeline runs.

    Subscribes to ``core.progress``; the bar advances as the pipeline calls
    ``stage()/advance()/set_pct()``. Renders a live rich bar on a TTY and
    single updates per phase elsewhere. Always unsubscribes itself.

    Args:
        description: Initial bar label.
    """
    console = Console()

    if not console.is_terminal:
        progress_hub.subscribe(_emit_plain)
        try:
            yield
        finally:
            progress_hub.unsubscribe(_emit_plain)
        return

    with Progress(
        TextColumn("[bold cyan]{task.description}[/bold cyan]", justify="left"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        console=console,
        expand=True,
    ) as bar:
        task = bar.add_task(description, total=100)

        def _update(pct: int, message: str) -> None:
            bar.update(task, completed=pct, description=message or description)

        progress_hub.subscribe(_update)
        try:
            yield
        finally:
            progress_hub.unsubscribe(_update)
            bar.update(task, completed=100, description="Scan complete")