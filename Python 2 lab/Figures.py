from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Shape(ABC):
    """Абстрактний графічний об'єкт редактора."""

    @abstractmethod
    def draw(self, canvas: tk.Canvas) -> None:
        """Відобразити об'єкт на полотні."""


@dataclass(frozen=True)
class Dot(Shape):
    center: Point

    def draw(self, canvas: tk.Canvas) -> None:
        radius = 3
        canvas.create_oval(
            self.center.x - radius,
            self.center.y - radius,
            self.center.x + radius,
            self.center.y + radius,
            fill="black",
            outline="black",
        )


@dataclass(frozen=True)
class Line(Shape):
    start: Point
    end: Point

    def draw(self, canvas: tk.Canvas) -> None:
        canvas.create_line(
            self.start.x,
            self.start.y,
            self.end.x,
            self.end.y,
            fill="black",
            width=2,
        )

@dataclass(frozen=True)
class Rectangle(Shape):
    first_corner: Point
    opposite_corner: Point

    def draw(self, canvas: tk.Canvas) -> None:
        canvas.create_rectangle(
            self.first_corner.x,
            self.first_corner.y,
            self.opposite_corner.x,
            self.opposite_corner.y,
            outline="black",
            width=2,
            fill="white",
        )

@dataclass(frozen=True)
class Ellipse(Shape):
    center: Point
    corner: Point

    def draw(self, canvas: tk.Canvas) -> None:
        radius_x = abs(self.corner.x - self.center.x)
        radius_y = abs(self.corner.y - self.center.y)
        canvas.create_oval(
            self.center.x - radius_x,
            self.center.y - radius_y,
            self.center.x + radius_x,
            self.center.y + radius_y,
            outline="black",
            width=2,
        )
