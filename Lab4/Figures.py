from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


class Shape(ABC):
    @abstractmethod
    def show(self, canvas: tk.Canvas) -> None:
        """Display the shape on the canvas."""


@dataclass(frozen=True)
class DotShape(Shape):
    center: Point

    def show(self, canvas: tk.Canvas) -> None:
        radius = 3
        canvas.create_oval(
            self.center.x - radius,
            self.center.y - radius,
            self.center.x + radius,
            self.center.y + radius,
            fill="#202020",
            outline="#202020",
        )


@dataclass(frozen=True)
class LineShape(Shape):
    start: Point
    end: Point

    def show(self, canvas: tk.Canvas) -> None:
        canvas.create_line(
            self.start.x,
            self.start.y,
            self.end.x,
            self.end.y,
            fill="#202020",
            width=2,
        )


@dataclass(frozen=True)
class RectShape(Shape):
    first_corner: Point
    opposite_corner: Point

    def show(self, canvas: tk.Canvas) -> None:
        canvas.create_rectangle(
            self.first_corner.x,
            self.first_corner.y,
            self.opposite_corner.x,
            self.opposite_corner.y,
            outline="#202020",
            width=2,
            fill="white",
        )


@dataclass(frozen=True)
class EllipseShape(Shape):
    center: Point
    corner: Point

    def show(self, canvas: tk.Canvas) -> None:
        radius_x = abs(self.corner.x - self.center.x)
        radius_y = abs(self.corner.y - self.center.y)
        canvas.create_oval(
            self.center.x - radius_x,
            self.center.y - radius_y,
            self.center.x + radius_x,
            self.center.y + radius_y,
            outline="#202020",
            width=2,
        )


class LineWithCircles(LineShape, EllipseShape):
    """A line whose endpoints are marked with circles."""

    def __init__(self, start: Point, end: Point) -> None:
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    def show(self, canvas: tk.Canvas) -> None:
        LineShape.show(self, canvas)
        radius = 5
        for point in (self.start, self.end):
            circle = EllipseShape(
                point,
                Point(point.x + radius, point.y + radius),
            )
            circle.show(canvas)


class WireframeCube(RectShape, LineShape):
    """A perspective wireframe cube built from rectangles and lines."""

    def __init__(self, first_corner: Point, opposite_corner: Point) -> None:
        object.__setattr__(self, "first_corner", first_corner)
        object.__setattr__(self, "opposite_corner", opposite_corner)

    def show(self, canvas: tk.Canvas) -> None:
        width = abs(self.opposite_corner.x - self.first_corner.x)
        height = abs(self.opposite_corner.y - self.first_corner.y)
        side = min(width, height)
        left = min(self.first_corner.x, self.opposite_corner.x)
        top = min(self.first_corner.y, self.opposite_corner.y)
        right = left + side
        bottom = top + side
        depth = side * 0.35
        RectShape(Point(left, top), Point(right, bottom)).show(canvas)
        back_left = left + depth
        back_right = right + depth
        back_top = top - depth
        back_bottom = bottom - depth
        RectShape(
            Point(back_left, back_top),
            Point(back_right, back_bottom),
        ).show(canvas)
        edges = (
            ((left, top), (right, top)),
            ((right, top), (right, bottom)),
            ((right, bottom), (left, bottom)),
            ((left, bottom), (left, top)),
            ((back_left, back_top), (back_right, back_top)),
            ((back_right, back_top), (back_right, back_bottom)),
            ((back_right, back_bottom), (back_left, back_bottom)),
            ((back_left, back_bottom), (back_left, back_top)),
            ((left, top), (back_left, back_top)),
            ((right, top), (back_right, back_top)),
            ((left, bottom), (back_left, back_bottom)),
            ((right, bottom), (back_right, back_bottom)),
        )
        for start, end in edges:
            LineShape(
                Point(*start),
                Point(*end),
            ).show(canvas)
