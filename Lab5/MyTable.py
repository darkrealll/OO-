from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Sequence


Row = tuple[str, float, float, float, float]


class MyTable:
    """A model-independent, non-modal table window."""

    def __init__(
        self,
        parent: tk.Misc,
        on_select: Callable[[int], None],
        on_delete: Callable[[int], None],
    ) -> None:
        self._on_select = on_select
        self._on_delete = on_delete
        self._window: Optional[tk.Toplevel] = None
        self._table: Optional[ttk.Treeview] = None
        self._rows: list[Row] = []
        self._parent = parent

    def show(self, rows: Sequence[Row]) -> None:
        self._rows = list(rows)
        if self._window is None or not self._window.winfo_exists():
            self._window = tk.Toplevel(self._parent)
            self._window.title("Таблиця об'єктів")
            self._window.geometry("620x300")
            self._window.protocol("WM_DELETE_WINDOW", self.close)
            self._table = ttk.Treeview(
                self._window,
                columns=("name", "x1", "y1", "x2", "y2"),
                show="headings",
                selectmode="browse",
            )
            headings = (("name", "Назва"), ("x1", "x1"), ("y1", "y1"),
                        ("x2", "x2"), ("y2", "y2"))
            for column, title in headings:
                self._table.heading(column, text=title)
                self._table.column(column, width=110, anchor="center")
            self._table.column("name", width=220, anchor="w")
            self._table.pack(fill="both", expand=True, padx=8, pady=(8, 4))
            self._table.bind("<<TreeviewSelect>>", self._selected)
            tk.Button(
                self._window, text="Вилучити виділений", command=self._delete,
            ).pack(pady=(0, 8))
        self._refresh()
        self._window.deiconify()
        self._window.lift()

    def _refresh(self) -> None:
        if self._table is None:
            return
        selected = self._table.selection()
        selected_index = selected[0] if selected else None
        for item in self._table.get_children():
            self._table.delete(item)
        for index, row in enumerate(self._rows):
            self._table.insert("", "end", iid=str(index), values=row)
        if selected_index is not None and int(selected_index) < len(self._rows):
            self._table.selection_set(selected_index)
            self._table.focus(selected_index)

    def _selected(self, _event: tk.Event) -> None:
        del _event
        if self._table is None:
            return
        selected = self._table.selection()
        if selected:
            self._on_select(int(selected[0]))

    def _delete(self) -> None:
        if self._table is None:
            return
        selected = self._table.selection()
        if selected:
            self._on_delete(int(selected[0]))

    def update(self, rows: Sequence[Row]) -> None:
        self._rows = list(rows)
        if self._window is not None and self._window.winfo_exists():
            self._refresh()

    def close(self) -> None:
        if self._window is not None and self._window.winfo_exists():
            self._window.destroy()
        self._window = None
        self._table = None

    def destroy(self) -> None:
        self.close()
