"""
Утилиты для преобразования координат
"""


def x_to_screen(x, area_x, area_size, x_min, x_max):
    """
    Преобразует логическую координату X в экранный пиксель.
    """
    return area_x + ((x - x_min) / (x_max - x_min)) * area_size


def y_to_screen(y, area_y, area_size, y_min, y_max):
    """
    Преобразует логическую координату Y в экранный пиксель.
    """
    normalized_y = (y - y_min) / (y_max - y_min)
    return area_y + normalized_y * area_size