import tkinter as tk
from tkinter import ttk


class FirstPageDialog:
    """Первое окно Робота1: переход далее или отмена."""

    def __init__(self, parent: tk.Misc) -> None:
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Робота1 - сторінка 1")
        self._dialog.geometry("320x130")
        self._dialog.resizable(False, False)
        self._dialog.transient(parent)
        self._action = "cancel"
        self._build_view()

    def _build_view(self) -> None:
        ttk.Label(self._dialog, text="Перше діалогове вікно").pack(pady=(22, 12))
        buttons = ttk.Frame(self._dialog)
        buttons.pack()
        ttk.Button(buttons, text="Далі >", command=self._go_next).pack(side="left", padx=4)
        ttk.Button(buttons, text="Відміна", command=self._close).pack(side="left", padx=4)
        self._dialog.protocol("WM_DELETE_WINDOW", self._close)

    def _go_next(self) -> None:
        self._action = "next"
        self._dialog.destroy()

    def _close(self) -> None:
        self._action = "cancel"
        self._dialog.destroy()

    def show(self) -> str:
        self._dialog.grab_set()
        self._dialog.wait_window()
        return self._action