# graph_widget.py
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
import math

class GraphWidget(Widget):
    """Виджет для рисования графика"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.function = None
        self.x_min = -5
        self.x_max = 5
        self.y_min = -5
        self.y_max = 5
        self.points = []
        self.graph_padding = dp(20)
        self.bind(size=self.on_size, pos=self.on_size)

    def on_size(self, *args):
        self.draw()

    def set_function(self, func):
        self.function = func
        self.draw()

    def set_ranges(self, x_min, x_max, y_min, y_max):
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        if self.function:
            self.draw()

    def draw(self):
        self.canvas.clear()
        self.points = []
        if not self.function:
            return

        self.graph_area = (
            self.x + self.graph_padding,
            self.y + self.graph_padding,
            self.width - 2 * self.graph_padding,
            self.height - 2 * self.graph_padding
        )
        graph_x, graph_y, graph_width, graph_height = self.graph_area
        side = min(graph_width, graph_height)
        square_x = graph_x + (graph_width - side) / 2
        square_y = graph_y + (graph_height - side) / 2
        square_size = side

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=(square_x, square_y), size=(square_size, square_size))
            Color(0.9, 0.9, 0.9, 0.5)
            self._draw_grid(square_x, square_y, square_size, square_size)
            Color(0.3, 0.3, 0.3, 1)
            self._draw_axes(square_x, square_y, square_size, square_size)
            Color(0.4, 0.35, 0.85, 1)
            self._draw_function(square_x, square_y, square_size, square_size)
            Color(0.8, 0.8, 0.8, 0.3)
            Line(rectangle=(square_x, square_y, square_size, square_size), width=1)

    def _draw_grid(self, area_x, area_y, area_size, area_height):
        x_pixels_per_unit = area_size / (self.x_max - self.x_min)
        y_pixels_per_unit = area_size / (self.y_max - self.y_min)
        pixels_per_unit = min(x_pixels_per_unit, y_pixels_per_unit)
        desired_lines = 10
        unit_step_x = (self.x_max - self.x_min) / desired_lines
        unit_step_y = (self.y_max - self.y_min) / desired_lines
        unit_step = max(unit_step_x, unit_step_y)
        unit_step = self._nice_number(unit_step)

        x_start = math.ceil(self.x_min / unit_step) * unit_step
        x_end = math.floor(self.x_max / unit_step) * unit_step
        x = x_start
        while x <= x_end + unit_step/100:
            screen_x = self._x_to_screen(x, area_x, area_size)
            if area_x <= screen_x <= area_x + area_size:
                Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=0.5)
            x += unit_step

        y_start = math.ceil(self.y_min / unit_step) * unit_step
        y_end = math.floor(self.y_max / unit_step) * unit_step
        y = y_start
        while y <= y_end + unit_step/100:
            screen_y = self._y_to_screen(y, area_y, area_size)
            if area_y <= screen_y <= area_y + area_size:
                Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=0.5)
            y += unit_step

    def _nice_number(self, value):
        if value <= 0:
            return 1.0
        exponent = math.floor(math.log10(value))
        fraction = value / (10 ** exponent)
        nice_fractions = [1, 2, 5, 10]
        nice_fraction = min(nice_fractions, key=lambda x: abs(x - fraction))
        return nice_fraction * (10 ** exponent)

    def _draw_axes(self, area_x, area_y, area_size, area_height):
        screen_y = self._y_to_screen(0, area_y, area_size)
        if area_y <= screen_y <= area_y + area_size:
            Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=1.5)
            arrow_size = 8
            Line(points=[
                area_x + area_size - arrow_size, screen_y - arrow_size/2,
                area_x + area_size, screen_y,
                area_x + area_size - arrow_size, screen_y + arrow_size/2
            ], width=1.5)

        screen_x = self._x_to_screen(0, area_x, area_size)
        if area_x <= screen_x <= area_x + area_size:
            Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=1.5)
            arrow_size = 8
            Line(points=[
                screen_x - arrow_size/2, area_y + area_size - arrow_size,
                screen_x, area_y + area_size,
                screen_x + arrow_size/2, area_y + area_size - arrow_size
            ], width=1.5)

    def _draw_function(self, area_x, area_y, area_size, area_height):
        if not self.function:
            return
        points = []
        num_points = int(area_size * 2)
        for i in range(num_points + 1):
            x = self.x_min + (i / num_points) * (self.x_max - self.x_min)
            try:
                y = self.function(x)
                if math.isinf(y):
                    if len(points) > 2:
                        Line(points=points, width=2.5)
                    points = []
                    self.points.append(None)
                    continue
                if not math.isnan(y):
                    screen_x = self._x_to_screen(x, area_x, area_size)
                    screen_y = self._y_to_screen(y, area_y, area_size)
                    margin = 0
                    if (area_y - margin <= screen_y <= area_y + area_size + margin and
                        area_x - margin <= screen_x <= area_x + area_size + margin):
                        points.append(screen_x)
                        points.append(screen_y)
                        self.points.append((x, y))
                else:
                    if len(points) > 2:
                        Line(points=points, width=2.5)
                    points = []
                    self.points.append(None)
            except Exception:
                if len(points) > 2:
                    Line(points=points, width=2.5)
                points = []
                self.points.append(None)
                continue
        if len(points) > 2:
            Line(points=points, width=2.5)
        elif len(points) == 2:
            Line(points=points, width=2.5)

    def _x_to_screen(self, x, area_x, area_size):
        return area_x + ((x - self.x_min) / (self.x_max - self.x_min)) * area_size

    def _y_to_screen(self, y, area_y, area_size):
        normalized_y = (y - self.y_min) / (self.y_max - self.y_min)
        return area_y + normalized_y * area_size