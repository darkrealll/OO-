import tkinter as tk
from tkinter import ttk


class GroupDialog:
    """Диалог выбора группы факультета из списка."""

    GROUPS = ("КН-21", "КН-22", "ПІ-21", "ПІ-22", "КІ-21")

    def __init__(self, parent: tk.Misc) -> None:
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Робота2")
        self._dialog.geometry("300x240")
        self._dialog.resizable(False, False)
        self._dialog.transient(parent)
        self._result: str | None = None
        self._build_view()

    def _build_view(self) -> None:
        ttk.Label(self._dialog, text="Виберіть групу факультету:").pack(pady=(12, 6))
        self._group_list = tk.Listbox(self._dialog, height=6, exportselection=False)
        self._group_list.pack(fill="x", padx=25)
        for group in self.GROUPS:
            self._group_list.insert(tk.END, group)
        self._group_list.selection_set(0)

        buttons = ttk.Frame(self._dialog)
        buttons.pack(pady=12)
        ttk.Button(buttons, text="Так", command=self._accept).pack(side="left", padx=4)
        ttk.Button(buttons, text="Відміна", command=self._close).pack(side="left", padx=4)
        self._dialog.protocol("WM_DELETE_WINDOW", self._close)

    def _accept(self) -> None:
        selected = self._group_list.curselection()
        if selected:
            self._result = self._group_list.get(selected[0])
        self._dialog.destroy()

    def _close(self) -> None:
        self._result = None
        self._dialog.destroy()

    def show(self) -> str | None:
        self._dialog.grab_set()
        self._dialog.wait_window()
        return self._result