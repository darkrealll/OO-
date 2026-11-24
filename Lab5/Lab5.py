from __future__ import annotations

import csv
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable, Optional

from Figures import (
    DotShape, EllipseShape, LineShape, LineWithCircles, Point, RectShape,
    Shape, WireframeCube,
)
from MyTable import MyTable, Row


JOURNAL_NUMBER = 10
SHAPE_CAPACITY = JOURNAL_NUMBER + 100
RUBBER_COLOR = "#1565c0"


class ShapeStorage:
    def __init__(self, capacity: int) -> None:
        self._items: list[Shape] = []
        self._capacity = capacity

    @property
    def items(self) -> list[Shape]:
        return list(self._items)

    def add(self, shape: Shape) -> None:
        if len(self._items) >= self._capacity:
            raise OverflowError("Досягнуто максимальну кількість об'єктів.")
        self._items.append(shape)

    def remove(self, index: int) -> None:
        del self._items[index]

    def replace(self, shapes: list[Shape]) -> None:
        if len(shapes) > self._capacity:
            raise OverflowError("Файл містить більше об'єктів, ніж дозволено.")
        self._items = shapes

    def show_all(self, canvas: tk.Canvas) -> None:
        for shape in self._items:
            shape.show(canvas)

    def clear(self) -> None:
        self._items.clear()


class MyEditor:
    _instance: Optional[MyEditor] = None
    TOOLS = (
        ("Крапка", "dot"), ("Лінія", "line"), ("Прямокутник", "rectangle"),
        ("Еліпс", "ellipse"), ("Лінія з кружечками", "line_circles"),
        ("Каркас куба", "cube"),
    )
    CONSTRUCTORS: dict[str, Callable[[Point, Point], Shape]] = {
        "Лінія": LineShape, "Прямокутник": RectShape, "Еліпс": EllipseShape,
        "Лінія з кружечками": LineWithCircles, "Каркас куба": WireframeCube,
    }

    def __new__(cls) -> MyEditor:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._window = tk.Tk()
        self._window.title("Lab5 - графічний редактор")
        self._window.geometry("860x560")
        self._window.minsize(600, 400)
        self._storage = ShapeStorage(SHAPE_CAPACITY)
        self._current_type = 0
        self._object_var = tk.IntVar(value=0)
        self._start: Optional[Point] = None
        self._selected_index: Optional[int] = None
        self._table = MyTable(self._window, self._select_row, self._delete_row)
        self._menu = tk.Menu(self._window)
        self._objects_menu = tk.Menu(
            self._menu, tearoff=False, postcommand=self._sync_menu_selection,
        )
        self._create_menu()
        self._create_toolbar()
        self._canvas = tk.Canvas(self._window, background="white", cursor="crosshair")
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<ButtonPress-1>", self._start_object)
        self._canvas.bind("<B1-Motion>", self._preview_object)
        self._canvas.bind("<ButtonRelease-1>", self._finish_object)

    def _create_menu(self) -> None:
        file_menu = tk.Menu(self._menu, tearoff=False)
        file_menu.add_command(label="Очистити", command=self._clear)
        file_menu.add_command(label="Зберегти...", command=self._save)
        file_menu.add_command(label="Завантажити...", command=self._load)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.destroy)
        self._menu.add_cascade(label="Файл", menu=file_menu)
        for index, (name, _) in enumerate(self.TOOLS):
            self._objects_menu.add_radiobutton(
                label=name, variable=self._object_var, value=index,
                command=lambda selected=index: self._select_tool(selected),
            )
        self._menu.add_cascade(label="Об'єкти", menu=self._objects_menu)
        table_menu = tk.Menu(self._menu, tearoff=False)
        table_menu.add_command(label="Відкрити таблицю", command=self._show_table)
        table_menu.add_command(label="Закрити таблицю", command=self._table.close)
        self._menu.add_cascade(label="Таблиця", menu=table_menu)
        help_menu = tk.Menu(self._menu, tearoff=False)
        help_menu.add_command(label="Про програму", command=self._show_about)
        self._menu.add_cascade(label="Довідка", menu=help_menu)
        self._window.config(menu=self._menu)

    def _create_toolbar(self) -> None:
        toolbar = tk.Frame(self._window, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill="x", side="top")
        for index, (name, _) in enumerate(self.TOOLS):
            button = tk.Button(
                toolbar, text=name, command=lambda selected=index: self._select_tool(selected),
            )
            button.pack(side="left", padx=1, pady=1)

    def _sync_menu_selection(self) -> None:
        self._object_var.set(self._current_type)

    def _select_tool(self, tool: int) -> None:
        self._current_type = tool
        self._object_var.set(tool)
        self._start = None
        self._canvas.delete("preview")

    @staticmethod
    def _point_from_event(event: tk.Event) -> Point:
        return Point(float(event.x), float(event.y))

    def _start_object(self, event: tk.Event) -> None:
        point = self._point_from_event(event)
        if self._current_type == 0:
            self._add_shape(DotShape(point))
        else:
            self._start = point

    def _preview_object(self, event: tk.Event) -> None:
        if self._start is None:
            return
        self._canvas.delete("preview")
        start, end = self._start, self._point_from_event(event)
        kind = self.TOOLS[self._current_type][1]
        if kind in ("line", "line_circles"):
            self._canvas.create_line(start.x, start.y, end.x, end.y,
                                     fill=RUBBER_COLOR, dash=(5, 3), tags="preview")
        elif kind == "rectangle":
            self._canvas.create_rectangle(start.x, start.y, end.x, end.y,
                                          outline=RUBBER_COLOR, dash=(5, 3), tags="preview")
        elif kind == "ellipse":
            self._canvas.create_oval(start.x - abs(end.x - start.x),
                                     start.y - abs(end.y - start.y),
                                     start.x + abs(end.x - start.x),
                                     start.y + abs(end.y - start.y),
                                     outline=RUBBER_COLOR, dash=(5, 3), tags="preview")
        else:
            left, top = min(start.x, end.x), min(start.y, end.y)
            side = min(abs(end.x - start.x), abs(end.y - start.y))
            self._canvas.create_rectangle(left, top, left + side, top + side,
                                          outline=RUBBER_COLOR, dash=(5, 3), tags="preview")

    def _finish_object(self, event: tk.Event) -> None:
        if self._start is None:
            return
        start, end = self._start, self._point_from_event(event)
        self._start = None
        self._canvas.delete("preview")
        name = self.TOOLS[self._current_type][0]
        if name != "Крапка":
            self._add_shape(self.CONSTRUCTORS[name](start, end))

    def _add_shape(self, shape: Shape) -> None:
        try:
            self._storage.add(shape)
        except OverflowError as error:
            messagebox.showerror("Помилка", str(error), parent=self._window)
            return
        self._selected_index = None
        self._redraw()

    def _rows(self) -> list[Row]:
        return [shape.record() for shape in self._storage.items]

    def _redraw(self, update_table: bool = True) -> None:
        self._canvas.delete("all")
        self._storage.show_all(self._canvas)
        if self._selected_index is not None and self._selected_index < len(self._storage.items):
            row = self._rows()[self._selected_index]
            x1, y1, x2, y2 = row[1:]
            self._canvas.create_rectangle(
                min(x1, x2) - 6, min(y1, y2) - 6, max(x1, x2) + 6, max(y1, y2) + 6,
                outline=RUBBER_COLOR, dash=(3, 2), tags="selection",
            )
        if update_table:
            self._table.update(self._rows())

    def _show_table(self) -> None:
        self._table.show(self._rows())

    def _select_row(self, index: int) -> None:
        self._selected_index = index
        self._redraw(update_table=False)

    def _delete_row(self, index: int) -> None:
        if 0 <= index < len(self._storage.items):
            self._storage.remove(index)
            self._selected_index = None
            self._redraw()

    def _clear(self) -> None:
        self._storage.clear()
        self._selected_index = None
        self._redraw()

    def _save(self) -> None:
        filename = filedialog.asksaveasfilename(
            parent=self._window, defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not filename:
            return
        try:
            with Path(filename).open("w", newline="", encoding="utf-8-sig") as file:
                csv.writer(file).writerows(self._rows())
        except OSError as error:
            messagebox.showerror("Помилка збереження", str(error), parent=self._window)

    def _load(self) -> None:
        filename = filedialog.askopenfilename(
            parent=self._window, filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
        )
        if not filename:
            return
        try:
            shapes: list[Shape] = []
            with Path(filename).open(newline="", encoding="utf-8-sig") as file:
                for line_number, row in enumerate(csv.reader(file), start=1):
                    if len(row) != 5:
                        raise ValueError(f"Рядок {line_number}: потрібно 5 полів.")
                    name, x1, y1, x2, y2 = row
                    if name == "Крапка":
                        shapes.append(DotShape(Point(float(x1), float(y1))))
                    elif name in self.CONSTRUCTORS:
                        shapes.append(self.CONSTRUCTORS[name](
                            Point(float(x1), float(y1)), Point(float(x2), float(y2)),
                        ))
                    else:
                        raise ValueError(f"Рядок {line_number}: невідомий тип «{name}».")
            self._storage.replace(shapes)
            self._selected_index = None
            self._redraw()
        except (OSError, ValueError) as error:
            messagebox.showerror("Помилка завантаження", str(error), parent=self._window)

    def _show_about(self) -> None:
        messagebox.showinfo(
            "Про програму",
            f"Lab5 — графічний редактор об'єктів, варіант Ж={JOURNAL_NUMBER}.\n"
            "Таблиця, callback-виділення, видалення та CSV.",
            parent=self._window,
        )

    def run(self) -> None:
        self._window.mainloop()

    def destroy(self) -> None:
        self._table.destroy()
        if self._window.winfo_exists():
            self._window.destroy()
        self._initialized = False
        MyEditor._instance = None


def main() -> None:
    editor = MyEditor()
    try:
        editor.run()
    finally:
        editor.destroy()
        del editor


if __name__ == "__main__":
    main()
