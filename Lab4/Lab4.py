from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional

from Figures import (
    DotShape,
    EllipseShape,
    LineShape,
    LineWithCircles,
    Point,
    RectShape,
    Shape,
    WireframeCube,
)


JOURNAL_NUMBER = 10
SHAPE_CAPACITY = JOURNAL_NUMBER + 100
RUBBER_COLOR = "#1565c0"


class ShapeStorage:
    def __init__(self, capacity: int) -> None:
        self._items: list[Shape] = []
        self._capacity = capacity

    def add(self, shape: Shape) -> None:
        if len(self._items) >= self._capacity:
            raise OverflowError("Досягнуто максимальну кількість об'єктів.")
        self._items.append(shape)

    def show_all(self, canvas: tk.Canvas) -> None:
        for shape in self._items:
            shape.show(canvas)

    def clear(self) -> None:
        self._items.clear()


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text = text
        self._window: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event: tk.Event) -> None:
        del _event
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
        del _event
        if self._window is not None:
            self._window.destroy()
            self._window = None


class MyEditor:
    TOOLS = (
        ("Крапка", "dot"),
        ("Лінія", "line"),
        ("Прямокутник", "rectangle"),
        ("Еліпс", "ellipse"),
        ("Лінія з кружечками", "line_circles"),
        ("Каркас куба", "cube"),
    )

    def __init__(self) -> None:
        self._window = tk.Tk()
        self._window.title("Lab4 - графічний редактор")
        self._window.geometry("860x560")
        self._window.minsize(600, 400)
        self._storage = ShapeStorage(SHAPE_CAPACITY)
        self._current_type = 0
        self._object_var = tk.IntVar(value=0)
        self._start: Optional[Point] = None
        self._menu = tk.Menu(self._window)
        self._objects_menu = tk.Menu(
            self._menu,
            tearoff=False,
            postcommand=self._sync_menu_selection,
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
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self._window.destroy)
        self._menu.add_cascade(label="Файл", menu=file_menu)

        for index, (name, _) in enumerate(self.TOOLS):
            self._objects_menu.add_radiobutton(
                label=name,
                variable=self._object_var,
                value=index,
                command=lambda selected=index: self._select_tool(selected),
            )
        self._menu.add_cascade(label="Об'єкти", menu=self._objects_menu)

        help_menu = tk.Menu(self._menu, tearoff=False)
        help_menu.add_command(label="Про програму", command=self._show_about)
        self._menu.add_cascade(label="Довідка", menu=help_menu)
        self._window.config(menu=self._menu)

    def _create_toolbar(self) -> None:
        toolbar = tk.Frame(self._window, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill="x", side="top")
        self._icons = [self._make_icon(kind) for _, kind in self.TOOLS]
        for index, (name, _) in enumerate(self.TOOLS):
            button = tk.Button(
                toolbar,
                image=self._icons[index],
                width=28,
                height=28,
                command=lambda selected=index: self._select_tool(selected),
            )
            button.pack(side="left", padx=1, pady=1)
            ToolTip(button, name)

    def _make_icon(self, kind: str) -> tk.PhotoImage:
        icon = tk.PhotoImage(width=24, height=24)
        icon.put("#f0f0f0", to=(0, 0, 24, 24))
        if kind == "dot":
            icon.put("#202020", to=(10, 10, 14, 14))
        elif kind == "line":
            icon.put("#202020", to=(4, 18, 20, 20))
        elif kind == "rectangle":
            icon.put("#202020", to=(4, 5, 20, 7))
            icon.put("#202020", to=(4, 17, 20, 19))
            icon.put("#202020", to=(4, 5, 6, 19))
            icon.put("#202020", to=(18, 5, 20, 19))
        elif kind == "ellipse":
            for x in range(4, 21):
                for y in range(5, 20):
                    dx = (x - 12) / 8
                    dy = (y - 12) / 7
                    if 0.8 <= dx * dx + dy * dy <= 1.25:
                        icon.put("#202020", (x, y))
        elif kind == "line_circles":
            icon.put("#1565c0", to=(5, 11, 19, 13))
            icon.put("#1565c0", to=(3, 8, 8, 16))
            icon.put("#1565c0", to=(16, 8, 21, 16))
        else:
            color = "#7b1fa2"

            def draw_segment(
                start: tuple[int, int],
                end: tuple[int, int],
            ) -> None:
                x1, y1 = start
                x2, y2 = end
                steps = max(abs(x2 - x1), abs(y2 - y1))
                for step in range(steps + 1):
                    ratio = step / steps
                    x = round(x1 + (x2 - x1) * ratio)
                    y = round(y1 + (y2 - y1) * ratio)
                    icon.put(color, (x, y))

            for segment in (
                ((5, 8), (16, 8)),
                ((16, 8), (16, 19)),
                ((16, 19), (5, 19)),
                ((5, 19), (5, 8)),
                ((9, 5), (20, 5)),
                ((20, 5), (20, 16)),
                ((20, 16), (9, 16)),
                ((9, 16), (9, 5)),
                ((5, 8), (9, 5)),
                ((16, 8), (20, 5)),
                ((16, 19), (20, 16)),
                ((5, 19), (9, 16)),
            ):
                draw_segment(*segment)
        return icon

    def _sync_menu_selection(self) -> None:
        self._object_var.set(self._current_type)

    def _select_tool(self, tool: int) -> None:
        self._current_type = tool
        self._object_var.set(tool)
        self._start = None
        self._canvas.delete("preview")

    def _point_from_event(self, event: tk.Event) -> Point:
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
        start = self._start
        end = self._point_from_event(event)
        kind = self.TOOLS[self._current_type][1]
        if kind in ("line", "line_circles"):
            self._canvas.create_line(
                start.x, start.y, end.x, end.y,
                fill=RUBBER_COLOR, dash=(5, 3), width=2, tags="preview",
            )
            if kind == "line_circles":
                for point in (start, end):
                    self._canvas.create_oval(
                        point.x - 5, point.y - 5, point.x + 5, point.y + 5,
                        outline=RUBBER_COLOR, dash=(5, 3), tags="preview",
                    )
        elif kind == "rectangle":
            self._canvas.create_rectangle(
                start.x, start.y, end.x, end.y,
                outline=RUBBER_COLOR, dash=(5, 3), width=2, tags="preview",
            )
        elif kind == "ellipse":
            radius_x = abs(end.x - start.x)
            radius_y = abs(end.y - start.y)
            self._canvas.create_oval(
                start.x - radius_x, start.y - radius_y,
                start.x + radius_x, start.y + radius_y,
                outline=RUBBER_COLOR, dash=(5, 3), width=2, tags="preview",
            )
        else:
            self._draw_cube_preview(start, end)

    def _draw_cube_preview(self, start: Point, end: Point) -> None:
        width = abs(end.x - start.x)
        height = abs(end.y - start.y)
        side = min(width, height)
        left = min(start.x, end.x)
        top = min(start.y, end.y)
        right = left + side
        bottom = top + side
        depth = side * 0.35
        back = (left + depth, top - depth, right + depth, bottom - depth)
        self._canvas.create_rectangle(
            left, top, right, bottom, outline=RUBBER_COLOR,
            dash=(5, 3), width=2, tags="preview",
        )
        self._canvas.create_rectangle(
            *back, outline=RUBBER_COLOR, dash=(5, 3), width=2, tags="preview",
        )
        for front, rear in (
            ((left, top), (back[0], back[1])),
            ((right, top), (back[2], back[1])),
            ((left, bottom), (back[0], back[3])),
            ((right, bottom), (back[2], back[3])),
        ):
            self._canvas.create_line(
                *front, *rear, fill=RUBBER_COLOR, dash=(5, 3),
                width=2, tags="preview",
            )

    def _finish_object(self, event: tk.Event) -> None:
        if self._start is None:
            return
        start = self._start
        end = self._point_from_event(event)
        self._start = None
        self._canvas.delete("preview")
        kind = self.TOOLS[self._current_type][1]
        constructors: dict[str, Callable[[Point, Point], Shape]] = {
            "line": LineShape,
            "rectangle": RectShape,
            "ellipse": EllipseShape,
            "line_circles": LineWithCircles,
            "cube": WireframeCube,
        }
        self._add_shape(constructors[kind](start, end))

    def _add_shape(self, shape: Shape) -> None:
        try:
            self._storage.add(shape)
        except OverflowError as error:
            messagebox.showerror("Помилка", str(error), parent=self._window)
            return
        self._redraw()

    def _redraw(self) -> None:
        self._canvas.delete("all")
        self._storage.show_all(self._canvas)

    def _clear(self) -> None:
        self._storage.clear()
        self._start = None
        self._redraw()

    def _show_about(self) -> None:
        messagebox.showinfo(
            "Про програму",
            "Lab4 — графічний редактор об'єктів.\n"
            f"Варіант: Ж={JOURNAL_NUMBER}, місткість: {SHAPE_CAPACITY}.\n"
            "Нові фігури: лінія з кружечками та каркас куба.",
            parent=self._window,
        )

    def run(self) -> None:
        self._window.mainloop()

    def destroy(self) -> None:
        self._window.destroy()


def main() -> None:
    editor = MyEditor()
    try:
        editor.run()
    finally:
        editor.destroy()
        del editor


if __name__ == "__main__":
    main()
