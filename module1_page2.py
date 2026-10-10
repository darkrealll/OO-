import tkinter as tk
from tkinter import ttk


class SecondPageDialog:
    """Второе окно Робота1: возврат, подтверждение или отмена."""

    def __init__(self, parent: tk.Misc) -> None:
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Робота1 - сторінка 2")
        self._dialog.geometry("320x130")
        self._dialog.resizable(False, False)
        self._dialog.transient(parent)
        self._action = "cancel"
        self._build_view()

    def _build_view(self) -> None:
        ttk.Label(self._dialog, text="Друге діалогове вікно").pack(pady=(22, 12))
        buttons = ttk.Frame(self._dialog)
        buttons.pack()
        ttk.Button(buttons, text="< Назад", command=self._go_back).pack(side="left", padx=4)
        ttk.Button(buttons, text="Так", command=self._accept).pack(side="left", padx=4)
        ttk.Button(buttons, text="Відміна", command=self._close).pack(side="left", padx=4)
        self._dialog.protocol("WM_DELETE_WINDOW", self._close)

    def _go_back(self) -> None:
        self._action = "back"
        self._dialog.destroy()

    def _accept(self) -> None:
        self._action = "accept"
        self._dialog.destroy()

    def _close(self) -> None:
        self._action = "cancel"
        self._dialog.destroy()

    def show(self) -> str:
        self._dialog.grab_set()
        self._dialog.wait_window()
        return self._action