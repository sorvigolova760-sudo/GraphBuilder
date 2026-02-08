"""
Модуль для поиска точек пересечения двух функций
"""
import numpy as np


def find_intersections(f1, f2, x_min, x_max, tolerance=1e-6):
    """
    Находит точки пересечения двух функций численно.

    Args:
        f1: первая функция
        f2: вторая функция
        x_min: минимальное значение x
        x_max: максимальное значение x
        tolerance: допустимая погрешность

    Returns:
        список точек пересечения [(x, y)]
    """
    intersections = []
    num_steps = 2000
    step = (x_max - x_min) / num_steps

    for i in range(num_steps):
        x1 = x_min + i * step
        x2 = x1 + step
        try:
            y1_1 = f1(x1)
            y1_2 = f2(x1)
            y2_1 = f1(x2)
            y2_2 = f2(x2)

            diff1 = y1_1 - y1_2
            diff2 = y2_1 - y2_2

            if diff1 * diff2 < 0:
                root = bisection_intersection(f1, f2, x1, x2, tolerance)
                if root is not None:
                    y_val = f1(root)
                    intersections.append((root, y_val))
            elif abs(diff1) < tolerance:
                intersections.append((x1, y1_1))
        except:
            continue

    unique = []
    for x, y in intersections:
        if not any(abs(x - ux) < 0.1 for ux, uy in unique):
            unique.append((x, y))
    return unique


def bisection_intersection(f1, f2, a, b, tol=1e-6, max_iter=50):
    """
    Бисекция для f1(x) - f2(x) = 0
    """
    try:
        fa = f1(a) - f2(a)
        fb = f1(b) - f2(b)
        if fa * fb > 0:
            return None

        for _ in range(max_iter):
            c = (a + b) / 2
            fc = f1(c) - f2(c)
            if abs(fc) < tol:
                return c
            if fa * fc < 0:
                b, fb = c, fc
            else:
                a, fa = c, fc
        return (a + b) / 2
    except:
        return None
