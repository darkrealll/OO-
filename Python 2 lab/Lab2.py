from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from Figures import Dot, Ellipse, Line, Point, Rectangle, Shape


JOURNAL_NUMBER = 10
SHAPE_CAPACITY = JOURNAL_NUMBER + 100
RUBBER_COLOR = "#0000ff"


class ShapeStorage:
    """Статичний масив Shape* з фіксованою місткістю варіанта."""

    def __init__(self, capacity: int) -> None:
        self._items: list[Optional[Shape]] = [None] * capacity
        self._size = 0

    def add(self, shape: Shape) -> None:
        if self._size == len(self._items):
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


class ObjectEditor:
    """Головне вікно графічного редактора для Ж=10."""

    OBJECT_NAMES = ("Крапка", "Лінія", "Прямокутник", "Еліпс")

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._window.title("Lab2 - графічний редактор")
        self._window.geometry("760x520")
        self._window.minsize(500, 350)

        self._canvas = tk.Canvas(self._window, background="white", cursor="crosshair")
        self._canvas.pack(fill="both", expand=True)
        self._storage = ShapeStorage(SHAPE_CAPACITY)
        self._current_type = 2
        self._object_var = tk.IntVar(value=self._current_type)
        self._start: Optional[Point] = None
        self._menu = tk.Menu(self._window)
        
        self._objects_menu = tk.Menu(self._menu, tearoff=False, postcommand=self._on_init_menu_popup)

        self._create_menu()
        self._canvas.bind("<ButtonPress-1>", self._start_object)
        self._canvas.bind("<B1-Motion>", self._preview_object)
        self._canvas.bind("<ButtonRelease-1>", self._finish_object)
        self._window.protocol("WM_DELETE_WINDOW", self._window.destroy)

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
        
        
        self._menu.add_cascade(
            label="Об'єкти",
            menu=self._objects_menu,
        )

        help_menu = tk.Menu(self._menu, tearoff=False)
        help_menu.add_command(label="Про програму", command=self._show_about)
        self._menu.add_cascade(label="Довідка", menu=help_menu)
        self._window.config(menu=self._menu)

    def _on_init_menu_popup(self) -> None:
        self._object_var.set(self._current_type)

    def _select_object(self, object_type: int) -> None:
        self._current_type = object_type
        self._start = None
        self._canvas.delete("preview")

    def _point_from_event(self, event: tk.Event) -> Point:
        return Point(float(event.x), float(event.y))

    def _start_object(self, event: tk.Event) -> None:
        point = self._point_from_event(event)
        if self._current_type == 0:
            self._add_shape(Dot(point))
            return
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
            "Lab2 — графічний редактор об'єктів.\n"
            "Варіант: Ж=10, місткість масиву: 110.",
            parent=self._window,
        )

    def run(self) -> None:
        self._window.mainloop()


if __name__ == "__main__":
    ObjectEditor().run()