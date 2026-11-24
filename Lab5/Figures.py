from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


class Shape(ABC):
    type_name = "Об'єкт"

    @abstractmethod
    def show(self, canvas: tk.Canvas) -> None:
        """Display the shape on the canvas."""

    @abstractmethod
    def record(self) -> tuple[str, float, float, float, float]:
        """Return the CSV representation of the shape."""


@dataclass(frozen=True)
class DotShape(Shape):
    center: Point
    type_name = "Крапка"

    def show(self, canvas: tk.Canvas) -> None:
        radius = 3
        canvas.create_oval(
            self.center.x - radius, self.center.y - radius,
            self.center.x + radius, self.center.y + radius,
            fill="#202020", outline="#202020",
        )

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.center.x, self.center.y,
                self.center.x, self.center.y)


@dataclass(frozen=True)
class LineShape(Shape):
    start: Point
    end: Point
    type_name = "Лінія"

    def show(self, canvas: tk.Canvas) -> None:
        canvas.create_line(
            self.start.x, self.start.y, self.end.x, self.end.y,
            fill="#202020", width=2,
        )

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.start.x, self.start.y,
                self.end.x, self.end.y)


@dataclass(frozen=True)
class RectShape(Shape):
    first_corner: Point
    opposite_corner: Point
    type_name = "Прямокутник"

    def show(self, canvas: tk.Canvas) -> None:
        canvas.create_rectangle(
            self.first_corner.x, self.first_corner.y,
            self.opposite_corner.x, self.opposite_corner.y,
            outline="#202020", width=2, fill="white",
        )

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.first_corner.x, self.first_corner.y,
                self.opposite_corner.x, self.opposite_corner.y)


@dataclass(frozen=True)
class EllipseShape(Shape):
    center: Point
    corner: Point
    type_name = "Еліпс"

    def show(self, canvas: tk.Canvas) -> None:
        radius_x = abs(self.corner.x - self.center.x)
        radius_y = abs(self.corner.y - self.center.y)
        canvas.create_oval(
            self.center.x - radius_x, self.center.y - radius_y,
            self.center.x + radius_x, self.center.y + radius_y,
            outline="#202020", width=2,
        )

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.center.x, self.center.y,
                self.corner.x, self.corner.y)


class LineWithCircles(LineShape, EllipseShape):
    type_name = "Лінія з кружечками"

    def __init__(self, start: Point, end: Point) -> None:
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    def show(self, canvas: tk.Canvas) -> None:
        LineShape.show(self, canvas)
        for point in (self.start, self.end):
            canvas.create_oval(
                point.x - 5, point.y - 5, point.x + 5, point.y + 5,
                outline="#1565c0", width=2,
            )

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.start.x, self.start.y,
                self.end.x, self.end.y)


class WireframeCube(RectShape, LineShape):
    type_name = "Каркас куба"

    def __init__(self, first_corner: Point, opposite_corner: Point) -> None:
        object.__setattr__(self, "first_corner", first_corner)
        object.__setattr__(self, "opposite_corner", opposite_corner)

    def show(self, canvas: tk.Canvas) -> None:
        width = abs(self.opposite_corner.x - self.first_corner.x)
        height = abs(self.opposite_corner.y - self.first_corner.y)
        side = min(width, height)
        left = min(self.first_corner.x, self.opposite_corner.x)
        top = min(self.first_corner.y, self.opposite_corner.y)
        right, bottom = left + side, top + side
        depth = side * 0.35
        RectShape(Point(left, top), Point(right, bottom)).show(canvas)
        back = (left + depth, top - depth, right + depth, bottom - depth)
        canvas.create_rectangle(*back, outline="#7b1fa2", width=2)
        for front, rear in (
            ((left, top), (back[0], back[1])),
            ((right, top), (back[2], back[1])),
            ((left, bottom), (back[0], back[3])),
            ((right, bottom), (back[2], back[3])),
        ):
            canvas.create_line(*front, *rear, fill="#7b1fa2", width=2)

    def record(self) -> tuple[str, float, float, float, float]:
        return (self.type_name, self.first_corner.x, self.first_corner.y,
                self.opposite_corner.x, self.opposite_corner.y)
