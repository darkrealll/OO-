from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from Figures import Dot, Ellipse, Line, Point, Rectangle, Shape


JOURNAL_NUMBER = 10
VARIANT = JOURNAL_NUMBER + 1
SHAPE_CAPACITY = VARIANT + 100
RUBBER_COLOR = "#0000ff"


class ShapeStorage:
    def __init__(self, capacity: int) -> None:
        self._items: list[Optional[Shape]] = [None] * capacity
        self._size = 0

    def add(self, shape: Shape) -> None:
        if self._size >= len(self._items):
            raise OverflowError("Досягнуто максимальну кількість об'єктів.")
        self._items[self._size] = shape
        self._size += 1

    def draw_all(self, canvas: tk.Canvas) -> None:
        for shape in self._items[: self._size]:
            if shape is not None:
                shape.draw(canvas)

    def clear(self) -> None:
        self._items = [None] * len(self._items)
        self._size = 0


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text = text
        self._window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event: tk.Event) -> None:
        if self._window is not None:
            return
        x = self._widget.winfo_rootx() + self._widget.winfo_width() + 4
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._window = tk.Toplevel(self._widget)
        self._window.wm_overrideredirect(True)
        self._window.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self._window,
            text=self._text,
            background="#ffffe1",
            relief="solid",
            borderwidth=1,
            padx=4,
            pady=2,
        ).pack()

    def _hide(self, _event: tk.Event) -> None:
        if self._window is not None:
            self._window.destroy()
            self._window = None


class ObjectEditor:
    OBJECT_NAMES = ("Крапка", "Лінія", "Прямокутник", "Еліпс")

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._window.title("Lab3 - графічний редактор")
        self._window.geometry("760x520")
        self._window.minsize(500, 350)

        self._storage = ShapeStorage(SHAPE_CAPACITY)
        self._current_type = 2
        self._object_var = tk.IntVar(value=self._current_type)
        self._start: Optional[Point] = None
        self._menu = tk.Menu(self._window)
        self._objects_menu = tk.Menu(
            self._menu,
            tearoff=False,
            postcommand=self._on_init_menu_popup,
        )

        self._create_menu()
        self._create_toolbar()
        self._canvas = tk.Canvas(
            self._window,
            background="white",
            cursor="crosshair",
        )
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<ButtonPress-1>", self._start_object)
        self._canvas.bind("<B1-Motion>", self._preview_object)
        self._canvas.bind("<ButtonRelease-1>", self._finish_object)

    def _create_menu(self) -> None:
        file_menu = tk.Menu(self._menu, tearoff=False)
        file_menu.add_command(label="Очистити", command=self._clear)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self._window.destroy)
        self._menu.add_cascade(label="Файл", menu=file_menu)

        for index, name in enumerate(self.OBJECT_NAMES):
            self._objects_menu.add_radiobutton(
                label=name,
                variable=self._object_var,
                value=index,
                command=lambda selected=index: self._select_object(selected),
            )
        self._menu.add_cascade(label="Об'єкти", menu=self._objects_menu)

        help_menu = tk.Menu(self._menu, tearoff=False)
        help_menu.add_command(label="Про програму", command=self._show_about)
        self._menu.add_cascade(label="Довідка", menu=help_menu)
        self._window.config(menu=self._menu)

    def _create_toolbar(self) -> None:
        toolbar = tk.Frame(self._window, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill="x", side="top")
        self._icons = [
            self._make_icon("dot"),
            self._make_icon("line"),
            self._make_icon("rectangle"),
            self._make_icon("ellipse"),
        ]
        for index, name in enumerate(self.OBJECT_NAMES):
            button = tk.Button(
                toolbar,
                image=self._icons[index],
                width=28,
                height=28,
                relief=tk.RAISED,
                command=lambda selected=index: self._select_object(selected),
            )
            button.pack(side="left", padx=1, pady=1)
            ToolTip(button, name)

    def _make_icon(self, kind: str) -> tk.PhotoImage:
        icon = tk.PhotoImage(width=24, height=24)
        icon.put("#f0f0f0", to=(0, 0, 24, 24))
        if kind == "dot":
            icon.put("#000000", to=(10, 10, 14, 14))
        elif kind == "line":
            for offset in range(3):
                icon.put(
                    "#000000",
                    to=(4 + offset, 19 - offset, 20 + offset, 20 - offset),
                )
        elif kind == "rectangle":
            icon.put("#000000", to=(4, 5, 20, 7))
            icon.put("#000000", to=(4, 17, 20, 19))
            icon.put("#000000", to=(4, 5, 6, 19))
            icon.put("#000000", to=(18, 5, 20, 19))
        else:
            for x in range(4, 21):
                for y in range(5, 20):
                    dx = (x - 12) / 8
                    dy = (y - 12) / 7
                    if 0.8 <= dx * dx + dy * dy <= 1.25:
                        icon.put("#000000", (x, y))
        return icon

    def _on_init_menu_popup(self) -> None:
        self._object_var.set(self._current_type)

    def _select_object(self, object_type: int) -> None:
        self._current_type = object_type
        self._object_var.set(object_type)
        self._start = None
        self._canvas.delete("preview")

    def _point_from_event(self, event: tk.Event) -> Point:
        return Point(float(event.x), float(event.y))

    def _start_object(self, event: tk.Event) -> None:
        point = self._point_from_event(event)
        if self._current_type == 0:
            self._add_shape(Dot(point))
        else:
            self._start = point

    def _preview_object(self, event: tk.Event) -> None:
        if self._start is None:
            return
        self._canvas.delete("preview")
        self._draw_temporary(self._start, self._point_from_event(event))

    def _finish_object(self, event: tk.Event) -> None:
        if self._start is None:
            return
        end = self._point_from_event(event)
        start = self._start
        self._start = None
        self._canvas.delete("preview")
        if self._current_type == 1:
            shape: Shape = Line(start, end)
        elif self._current_type == 2:
            shape = Rectangle(start, end)
        else:
            shape = Ellipse(start, end)
        self._add_shape(shape)

    def _draw_temporary(self, start: Point, end: Point) -> None:
        if self._current_type == 1:
            self._canvas.create_line(
                start.x, start.y, end.x, end.y,
                fill=RUBBER_COLOR, width=2, tags="preview",
            )
        elif self._current_type == 2:
            self._canvas.create_rectangle(
                start.x, start.y, end.x, end.y,
                outline=RUBBER_COLOR, width=2, tags="preview",
            )
        else:
            radius_x = abs(end.x - start.x)
            radius_y = abs(end.y - start.y)
            self._canvas.create_oval(
                start.x - radius_x, start.y - radius_y,
                start.x + radius_x, start.y + radius_y,
                outline=RUBBER_COLOR, width=2, tags="preview",
            )

    def _add_shape(self, shape: Shape) -> None:
        try:
            self._storage.add(shape)
        except OverflowError as error:
            messagebox.showerror("Помилка", str(error), parent=self._window)
            return
        self._redraw()

    def _redraw(self) -> None:
        self._canvas.delete("all")
        self._storage.draw_all(self._canvas)

    def _clear(self) -> None:
        self._storage.clear()
        self._start = None
        self._redraw()

    def _show_about(self) -> None:
        messagebox.showinfo(
            "Про програму",
            "Lab3 — графічний редактор об'єктів.\n"
            f"Варіант: Ж={VARIANT}, місткість масиву: {SHAPE_CAPACITY}.",
            parent=self._window,
        )

    def run(self) -> None:
        self._window.mainloop()


if __name__ == "__main__":
    ObjectEditor().run()
