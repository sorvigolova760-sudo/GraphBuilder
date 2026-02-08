"""
Модуль для отрисовки графика (линии, сетка, точки)
"""
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import dp
import math


def draw_function_lines(canvas, functions, x_min, x_max, y_min, y_max, graph_area, colors):
    """
    Рисует линии функций на холсте.
    """
    graph_x, graph_y, graph_width, graph_height = graph_area
    side = min(graph_width, graph_height)
    square_x = graph_x + (graph_width - side) / 2
    square_y = graph_y + (graph_height - side) / 2
    square_size = side

    for idx, func in enumerate(functions):
        points = []
        num_points = max(1000, int(square_size * 3))
        for i in range(num_points + 1):
            x = x_min + (i / num_points) * (x_max - x_min)
            try:
                y = func(x)
                if math.isnan(y) or math.isinf(y):
                    if len(points) > 2:
                        Color(*colors[idx])
                        Line(points=points, width=2.5, cap='round', joint='round')
                    points = []
                    continue

                if y < y_min or y > y_max:
                    if len(points) > 2:
                        Color(*colors[idx])
                        Line(points=points, width=2.5, cap='round', joint='round')
                    points = []
                    continue

                screen_x = _x_to_screen(x, square_x, square_size, x_min, x_max)
                screen_y = _y_to_screen(y, square_y, square_size, y_min, y_max)

                if square_x <= screen_x <= square_x + square_size:
                    points.append(screen_x)
                    points.append(screen_y)
                else:
                    if len(points) > 2:
                        Color(*colors[idx])
                        Line(points=points, width=2.5, cap='round', joint='round')
                    points = []

            except Exception:
                if len(points) > 2:
                    Color(*colors[idx])
                    Line(points=points, width=2.5, cap='round', joint='round')
                points = []
                continue

        if len(points) >= 2:
            Color(*colors[idx])
            Line(points=points, width=2.5, cap='round', joint='round')


def draw_parametric_line(canvas, x_func, y_func, t_min, t_max, x_min, x_max, y_min, y_max, graph_area):
    """
    Рисует параметрическую кривую на холсте.
    """
    graph_x, graph_y, graph_width, graph_height = graph_area
    side = min(graph_width, graph_height)
    square_x = graph_x + (graph_width - side) / 2
    square_y = graph_y + (graph_height - side) / 2
    square_size = side

    Color(0, 0.5, 1, 1)  # голубой
    points = []

    num_points = 2000
    valid_points = 0

    for i in range(num_points + 1):
        t = t_min + (i / num_points) * (t_max - t_min)
        try:
            x = x_func(t)
            y = y_func(t)

            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                if not (math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y)):
                    # Стандартное масштабирование
                    screen_x = _x_to_screen(x, square_x, square_size, x_min, x_max)
                    screen_y = _y_to_screen(y, square_y, square_size, y_min, y_max)

                    # Проверяем что точка в видимой области
                    if (square_x <= screen_x <= square_x + square_size and
                        square_y <= screen_y <= square_y + square_size):
                        points.extend([screen_x, screen_y])
                        valid_points += 1
        except Exception as e:
            continue

    if len(points) >= 4:
        Line(points=points, width=2.5, cap='round', joint='round')


def draw_intersection_points(canvas, intersection_points, graph_area, x_min, x_max, y_min, y_max):
    """
    Рисует точки пересечения на холсте.
    """
    graph_x, graph_y, graph_width, graph_height = graph_area
    side = min(graph_width, graph_height)
    square_x = graph_x + (graph_width - side) / 2
    square_y = graph_y + (graph_height - side) / 2
    square_size = side

    if intersection_points:
        Color(0, 0, 0)
        for x, y in intersection_points:
            screen_x = _x_to_screen(x, square_x, square_size, x_min, x_max)
            screen_y = _y_to_screen(y, square_y, square_size, y_min, y_max)
            if square_x <= screen_x <= square_x + square_size and square_y <= screen_y <= square_y + square_size:
                Ellipse(pos=(screen_x - 4, screen_y - 4), size=(8, 8))


def _x_to_screen(x, area_x, area_size, x_min, x_max):
    return area_x + ((x - x_min) / (x_max - x_min)) * area_size

def _y_to_screen(y, area_y, area_size, y_min, y_max):
    normalized_y = (y - y_min) / (y_max - y_min)
    return area_y + normalized_y * area_size