"""
Модуль для поиска нулей и экстремумов функции
"""
import numpy as np
import re
from sympy import solve, diff, symbols, N


def find_zeros(func, expr_sym, user_expr, x_min, x_max):
    """
    Поиск нулей функции.
    """
    x_sym = symbols('x')  # Добавлено определение x_sym
    zeros = []

    if expr_sym is not None:
        try:
            solutions = solve(expr_sym, x_sym)

            for sol in solutions:
                if sol.is_real or sol.is_real is None:
                    try:
                        val = float(N(sol))
                        if x_min <= val <= x_max:
                            zeros.append(val)
                    except (TypeError, ValueError):
                        continue

        except Exception as e:
            print(f"⚠️ Аналитический поиск нулей не удался: {e}")

    if not zeros:
        zeros = _numerical_zeros(func, x_min, x_max)

    zeros = sorted(list(set([round(z, 4) for z in zeros])))

    if zeros:
        return ", ".join([f"x = {z}" for z in zeros])
    else:
        return "Нулей нет на отрезке"


def _numerical_zeros(func, x_min, x_max):
    """
    Численный поиск нулей методом перебора с уточнением.
    """
    zeros = []
    step = (x_max - x_min) / 1000

    for i in range(1000):
        x1 = x_min + i * step
        x2 = x1 + step

        try:
            y1 = func(x1)
            y2 = func(x2)

            if np.isfinite(y1) and np.isfinite(y2):
                if y1 * y2 < 0:
                    zero = _bisect(func, x1, x2)
                    if zero is not None:
                        zeros.append(zero)
                elif abs(y1) < 1e-6:
                    zeros.append(x1)

        except:
            continue

    return zeros


def _bisect(func, a, b, tol=1e-6, max_iter=50):
    """
    Метод деления отрезка пополам для уточнения нуля.
    """
    try:
        for _ in range(max_iter):
            c = (a + b) / 2
            fc = func(c)

            if abs(fc) < tol or (b - a) / 2 < tol:
                return c

            fa = func(a)
            if fa * fc < 0:
                b = c
            else:
                a = c

        return (a + b) / 2
    except:
        return None


def find_extrema(func, derivative_sym, x_min, x_max):
    """
    Поиск экстремумов (комбинированный метод).
    """
    x_sym = symbols('x')  # Добавлено определение x_sym
    extrema = []

    if derivative_sym is not None:
        extrema = _analytical_extrema(derivative_sym, func, x_min, x_max)

    if not extrema:
        extrema = _numerical_extrema(func, x_min, x_max)

    if not extrema:
        return "Не найдены"

    lines = []
    for typ, x, y in sorted(extrema, key=lambda e: e[1])[:5]:
        label = "Максимум" if typ == 'max' else "Минимум"
        lines.append(f"{label} при x ≈ {x:.3f}, f(x) ≈ {y:.3f}")

    return "\n    ".join(lines)


def _analytical_extrema(derivative_sym, func, x_min, x_max):
    """
    Аналитический поиск через производную.
    """
    x_sym = symbols('x')  # Добавлено определение x_sym
    extrema = []

    try:
        critical_points = solve(derivative_sym, x_sym)

        for cp in critical_points:
            if cp.is_real or cp.is_real is None:
                try:
                    x_val = float(N(cp))

                    if not (x_min <= x_val <= x_max):
                        continue

                    y_val = func(x_val)

                    if not np.isfinite(y_val):
                        continue

                    second_deriv = diff(derivative_sym, x_sym)
                    second_val = float(N(second_deriv.subs(x_sym, cp)))

                    if second_val > 0:
                        extrema.append(('min', x_val, y_val))
                    elif second_val < 0:
                        extrema.append(('max', x_val, y_val))
                    else:
                        eps = 0.001
                        y_left = func(x_val - eps)
                        y_right = func(x_val + eps)

                        if y_val > y_left and y_val > y_right:
                            extrema.append(('max', x_val, y_val))
                        elif y_val < y_left and y_val < y_right:
                            extrema.append(('min', x_val, y_val))

                except (TypeError, ValueError):
                    continue

    except Exception as e:
        print(f"⚠️ Аналитический поиск экстремумов не удался: {e}")

    return extrema


def _numerical_extrema(func, x_min, x_max):
    """
    Численный поиск экстремумов.
    """
    extrema = []
    step = (x_max - x_min) / 500

    for i in range(1, 499):
        x0 = x_min + (i - 1) * step
        x1 = x_min + i * step
        x2 = x_min + (i + 1) * step

        try:
            y0 = func(x0)
            y1 = func(x1)
            y2 = func(x2)

            if not (np.isfinite(y0) and np.isfinite(y1) and np.isfinite(y2)):
                continue

            if y1 > y0 + 1e-9 and y1 > y2 + 1e-9:
                extrema.append(('max', x1, y1))
            elif y1 < y0 - 1e-9 and y1 < y2 - 1e-9:
                extrema.append(('min', x1, y1))

        except:
            continue

    filtered = []
    for e in extrema:
        if not any(abs(e[1] - f[1]) < step * 2 for f in filtered):
            filtered.append(e)

    return filtered