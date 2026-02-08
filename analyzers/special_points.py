"""
Модуль для анализа особых точек параметрической кривой
"""
import numpy as np
from sympy import solve, diff, symbols, N


def find_special_parametric_points(x_func, y_func, dx_dt_sym, dy_dt_sym, t_min, t_max):
    """
    Поиск особых точек параметрической кривой.
    """
    t_sym = symbols('t')  # Добавлено определение t_sym
    special = []

    try:
        # Точки где dx/dt = 0 (вертикальная касательная)
        if dx_dt_sym is not None:
            try:
                t_vertical = solve(dx_dt_sym, t_sym)
                for t in t_vertical:
                    if t.is_real or t.is_real is None:
                        t_val = float(N(t))
                        if t_min <= t_val <= t_max:
                            x_val = x_func(t_val)
                            y_val = y_func(t_val)
                            special.append(f"Вертикальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
            except:
                pass

        # Точки где dy/dt = 0 (горизонтальная касательная)
        if dy_dt_sym is not None:
            try:
                t_horizontal = solve(dy_dt_sym, t_sym)
                for t in t_horizontal:
                    if t.is_real or t.is_real is None:
                        t_val = float(N(t))
                        if t_min <= t_val <= t_max:
                            x_val = x_func(t_val)
                            y_val = y_func(t_val)
                            special.append(f"Горизонтальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
            except:
                pass

        # Точки где dx/dt = dy/dt = 0 (особая точка)
        if dx_dt_sym is not None and dy_dt_sym is not None:
            try:
                singular = solve([dx_dt_sym, dy_dt_sym], t_sym)
                for sol in singular:
                    if isinstance(sol, dict):
                        t_val = float(N(sol[t_sym]))
                    else:
                        t_val = float(N(sol))

                    if t_min <= t_val <= t_max:
                        x_val = x_func(t_val)
                        y_val = y_func(t_val)
                        special.append(f"Особая точка при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
            except:
                pass

        if special:
            return "\n    ".join(special[:5])  # Топ-5
        else:
            return "Не найдены"

    except Exception as e:
        print(f"⚠️ Ошибка поиска особых точек: {e}")
        return "Не определены"


def find_self_intersections(x_func, y_func, t_min, t_max):
    """
    Поиск самопересечений параметрической кривой.
    """
    # t_sym не используется напрямую в этой функции, но символ определен для консистентности
    # t_sym = symbols('t')
    try:
        ts = np.linspace(t_min, t_max, 500)
        points = {}
        intersections = []

        for t in ts:
            try:
                x = x_func(t)
                y = y_func(t)

                if not (np.isfinite(x) and np.isfinite(y)):
                    continue

                # Округляем для сравнения
                key = (round(x, 2), round(y, 2))

                if key in points:
                    # Проверяем что это не та же точка параметра
                    if abs(t - points[key]) > 0.1:
                        intersections.append((key[0], key[1], points[key], t))
                else:
                    points[key] = t

            except:
                continue

        if intersections:
            result = []
            for x, y, t1, t2 in intersections[:3]:  # Топ-3
                result.append(f"({x:.2f}, {y:.2f}) при t₁={t1:.2f}, t₂={t2:.2f}")
            return "\n    ".join(result)
        else:
            return "Не найдены"

    except Exception as e:
        print(f"⚠️ Ошибка поиска самопересечений: {e}")
        return "Не определены"


def find_curvature_extrema(x_func, y_func, dx_dt_sym, dy_dt_sym, t_min, t_max):
    """
    Поиск экстремумов кривизны.
    """
    t_sym = symbols('t')  # Добавлено определение t_sym
    try:
        # κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
        if dx_dt_sym is None or dy_dt_sym is None:
            return "Не определены"

        # Вторые производные
        d2x_dt2 = diff(dx_dt_sym, t_sym)
        d2y_dt2 = diff(dy_dt_sym, t_sym)

        # Численный поиск экстремумов кривизны
        ts = np.linspace(t_min, t_max, 500)
        curvatures = []

        for t in ts:
            try:
                dx = float(N(dx_dt_sym.subs(t_sym, t)))
                dy = float(N(dy_dt_sym.subs(t_sym, t)))
                d2x = float(N(d2x_dt2.subs(t_sym, t)))
                d2y = float(N(d2y_dt2.subs(t_sym, t)))

                numerator = abs(dx * d2y - dy * d2x)
                denominator = (dx**2 + dy**2)**(3/2)

                if denominator > 1e-9:
                    k = numerator / denominator
                    curvatures.append((t, k))
            except:
                continue

        if not curvatures:
            return "Не найдены"

        # Находим максимум и минимум кривизны
        curvatures.sort(key=lambda x: x[1])

        result = []
        if len(curvatures) > 0:
            t_min_k, k_min = curvatures[0]
            x_min, y_min = x_func(t_min_k), y_func(t_min_k)
            result.append(f"Минимум κ={k_min:.3f} при t={t_min_k:.2f}, ({x_min:.2f}, {y_min:.2f})")

        if len(curvatures) > 1:
            t_max_k, k_max = curvatures[-1]
            x_max, y_max = x_func(t_max_k), y_func(t_max_k)
            result.append(f"Максимум κ={k_max:.3f} при t={t_max_k:.2f}, ({x_max:.2f}, {y_max:.2f})")

        return "\n    ".join(result) if result else "Не найдены"

    except Exception as e:
        print(f"⚠️ Ошибка анализа кривизны: {e}")
        return "Не определены"


def identify_curve_type(x_expr_sym, y_expr_sym, x_func, y_func, t_min, t_max):
    """
    Определение типа параметрической кривой.
    """
    t_sym = symbols('t')  # Добавлено определение t_sym
    try:
        # Проверяем на окружность: x² + y² = r²
        if x_expr_sym is not None and y_expr_sym is not None:
            # Подставляем несколько значений t
            test_t = [0, np.pi/4, np.pi/2, np.pi, 3*np.pi/2]
            radii = []

            for t_val in test_t:
                try:
                    x = float(N(x_expr_sym.subs(t_sym, t_val)))
                    y = float(N(y_expr_sym.subs(t_sym, t_val)))
                    r = np.sqrt(x**2 + y**2)
                    radii.append(r)
                except:
                    continue

            if radii and max(radii) - min(radii) < 0.1:
                return f"Окружность (r ≈ {np.mean(radii):.2f})"

        # Проверяем на эллипс: (x/a)² + (y/b)² = 1
        # Ищем паттерн cos(t), sin(t)
        x_str = str(x_expr_sym).lower()
        y_str = str(y_expr_sym).lower()

        if 'cos' in x_str and 'sin' in y_str:
            return "Эллипс/Окружность"

        # Проверяем на спираль
        if ('cos' in x_str or 'sin' in x_str) and ('t*' in x_str or '*t' in x_str):
            return "Спираль"

        # Проверяем на циклоиду
        if ('t' in x_str and 'sin' in x_str) and ('cos' in y_str):
            return "Циклоида"

        # Проверяем на лиссажу
        if 'sin' in x_str and 'sin' in y_str:
            return "Фигура Лиссажу"

        return "Произвольная кривая"

    except Exception as e:
        print(f"⚠️ Ошибка определения типа кривой: {e}")
        return "Не определён"