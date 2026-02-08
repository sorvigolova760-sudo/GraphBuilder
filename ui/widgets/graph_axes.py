"""
Модуль для отрисовки осей и сетки графика
"""
from kivy.graphics import Color, Line, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
import math


def draw_axes_and_grid(canvas, x_min, x_max, y_min, y_max, graph_area):
    """
    Рисует оси координат, сетку и подписи на холсте.
    """
    graph_x, graph_y, graph_width, graph_height = graph_area
    side = min(graph_width, graph_height)
    square_x = graph_x + (graph_width - side) / 2
    square_y = graph_y + (graph_height - side) / 2
    square_size = side

    # Рисуем белый фон
    Color(1, 1, 1, 1)
    Rectangle(pos=(square_x, square_y), size=(square_size, square_size))

    # Рисуем сетку
    Color(0.6, 0.6, 0.6, 0.8)
    _draw_grid(canvas, x_min, x_max, y_min, y_max, square_x, square_y, square_size, square_size)

    # Рисуем оси
    Color(0.3, 0.3, 0.3, 1)
    _draw_axes(canvas, x_min, x_max, y_min, y_max, square_x, square_y, square_size, square_size)


def _draw_grid(canvas, x_min, x_max, y_min, y_max, area_x, area_y, area_size, area_height):
    x_pixels_per_unit = area_size / (x_max - x_min)
    y_pixels_per_unit = area_size / (y_max - y_min)
    pixels_per_unit = min(x_pixels_per_unit, y_pixels_per_unit)
    desired_lines = 10
    unit_step_x = (x_max - x_min) / desired_lines
    unit_step_y = (y_max - y_min) / desired_lines
    unit_step = max(unit_step_x, unit_step_y)
    unit_step = _nice_number(unit_step)

    x_start = math.ceil(x_min / unit_step) * unit_step
    x_end = math.floor(x_max / unit_step) * unit_step
    x = x_start
    while x <= x_end + unit_step/100:
        screen_x = _x_to_screen(x, area_x, area_size, x_min, x_max)
        if area_x <= screen_x <= area_x + area_size:
            Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=0.5)
        x += unit_step

    y_start = math.ceil(y_min / unit_step) * unit_step
    y_end = math.floor(y_max / unit_step) * unit_step
    y = y_start
    while y <= y_end + unit_step/100:
        screen_y = _y_to_screen(y, area_y, area_size, y_min, y_max)
        if area_y <= screen_y <= area_y + area_size:
            Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=0.5)
        y += unit_step


def _draw_axes(canvas, x_min, x_max, y_min, y_max, area_x, area_y, area_size, area_height):
    """
    Рисует оси координат с подписями
    """
    # Ось X (где y=0)
    screen_y = _y_to_screen(0, area_y, area_size, y_min, y_max)
    if area_y <= screen_y <= area_y + area_size:
        Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=1.5)
        arrow_size = 8
        Line(points=[
            area_x + area_size - arrow_size, screen_y - arrow_size/2,
            area_x + area_size, screen_y,
            area_x + area_size - arrow_size, screen_y + arrow_size/2
        ], width=1.5)

    # Ось Y (где x=0)
    screen_x = _x_to_screen(0, area_x, area_size, x_min, x_max)
    if area_x <= screen_x <= area_x + area_size:
        Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=1.5)
        arrow_size = 8
        Line(points=[
            screen_x - arrow_size/2, area_y + area_size - arrow_size,
            screen_x, area_y + area_size,
            screen_x + arrow_size/2, area_y + area_size - arrow_size
        ], width=1.5)

    _draw_axis_labels(canvas, x_min, x_max, y_min, y_max, area_x, area_y, area_size, area_height)


def _draw_axis_labels(canvas, x_min, x_max, y_min, y_max, area_x, area_y, area_size, area_height):
    """
    Рисует текстовые подписи рядом с осями координат
    """
    font_size = dp(12)
    label_color = (0.2, 0.2, 0.2, 1)

    # === Подписи на оси X ===
    x_unit_step = _nice_number((x_max - x_min) / 8)
    x_start = math.ceil(x_min / x_unit_step) * x_unit_step
    x_end = math.floor(x_max / x_unit_step) * x_unit_step
    x = x_start
    while x <= x_end + x_unit_step / 100:
        if abs(x) > 0.01:
            screen_x = _x_to_screen(x, area_x, area_size, x_min, x_max)
            screen_y_axis_x = _y_to_screen(0, area_y, area_size, y_min, y_max)

            if area_x <= screen_x <= area_x + area_size and area_y <= screen_y_axis_x <= area_y + area_size:
                label = CoreLabel(
                    text=str(round(x, 2)),
                    font_size=font_size,
                    color=label_color
                )
                label.refresh()
                texture = label.texture
                label_x = screen_x - texture.width / 2
                label_y = screen_y_axis_x - texture.height - dp(3)
                if label_y >= area_y - texture.height - dp(10):
                    Color(*label_color)
                    Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
        x += x_unit_step

    # === Подписи на оси Y ===
    y_unit_step = _nice_number((y_max - y_min) / 8)
    y_start = math.ceil(y_min / y_unit_step) * y_unit_step
    y_end = math.floor(y_max / y_unit_step) * y_unit_step
    y = y_start
    while y <= y_end + y_unit_step / 100:
        if abs(y) > 0.01:
            screen_y = _y_to_screen(y, area_y, area_size, y_min, y_max)
            screen_x_axis_y = _x_to_screen(0, area_x, area_size, x_min, x_max)

            if area_y <= screen_y <= area_y + area_size and area_x <= screen_x_axis_y <= area_x + area_size:
                label = CoreLabel(
                    text=str(round(y, 2)),
                    font_size=font_size,
                    color=label_color
                )
                label.refresh()
                texture = label.texture
                label_x = screen_x_axis_y - texture.width - dp(5)
                label_y = screen_y - texture.height / 2
                if label_x >= area_x - texture.width - dp(10):
                    Color(*label_color)
                    Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
        y += y_unit_step


def _nice_number(value):
    if value <= 0:
        return 1.0
    exponent = math.floor(math.log10(value))
    fraction = value / (10 ** exponent)
    nice_fractions = [1, 2, 5, 10]
    nice_fraction = min(nice_fractions, key=lambda x: abs(x - fraction))
    return nice_fraction * (10 ** exponent)


def _x_to_screen(x, area_x, area_size, x_min, x_max):
    return area_x + ((x - x_min) / (x_max - x_min)) * area_size

def _y_to_screen(y, area_y, area_size, y_min, y_max):
    normalized_y = (y - y_min) / (y_max - y_min)
    return area_y + normalized_y * area_size