"""
Анализатор для параметрических функций x = x(t), y = y(t)
"""
from .base_analyzer import BaseAnalyzer
from sympy import symbols, sympify, solve, S, simplify, diff
import numpy as np
import re

class ParametricAnalyzer(BaseAnalyzer):
    """
    Анализатор для параметрических функций x = x(t), y = y(t)
    """
    def __init__(self, x_func, y_func, x_expr, y_expr, t_min, t_max):
        """
        Args:
            x_func: функция x(t)
            y_func: функция y(t)
            x_expr: строковое выражение x(t)
            y_expr: строковое выражение y(t)
            t_min: минимальное значение параметра
            t_max: максимальное значение параметра
        """
        super().__init__(None, f"x(t)={x_expr}, y(t)={y_expr}", t_min, t_max, func_type='parametric')
        self.x_func = x_func
        self.y_func = y_func
        self.x_expr = x_expr
        self.y_expr = y_expr
        self.t_sym = symbols('t')
        self.x_expr_sym = None
        self.y_expr_sym = None
        self.dx_dt_sym = None
        self.dy_dt_sym = None
        self._parse_parametric_expressions()

    def _parse_parametric_expressions(self):
        """
        Парсинг параметрических выражений x(t) и y(t).
        """
        print(f"\n🔧 ПАРАМЕТРИЧЕСКИЙ РЕЖИМ")
        print(f"   x(t) = {self.x_expr}")
        print(f"   y(t) = {self.y_expr}")

        def parse_param_expr(expr_str):
            """
            Парсинг одного параметрического выражения.
            """
            expr = expr_str.lower().strip()

            # Заменяем степени
            expr = expr.replace('^', '**')
            expr = expr.replace('²', '**2')
            expr = expr.replace('³', '**3')

            # Убираем math. префиксы
            expr = re.sub(r'math\.', '', expr)

            # Замена функций
            expr = re.sub(r'\b(?:arcsin|asin)\(', 'asin(', expr)
            expr = re.sub(r'\b(?:arccos|acos)\(', 'acos(', expr)
            expr = re.sub(r'\b(?:arctan|atan)\(', 'atan(', expr)
            expr = re.sub(r'\bln\(', 'log(', expr)

            # Неявное умножение (заменяем x на t)
            expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
            expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
            expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
            expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)

            # Финальная очистка
            expr = re.sub(r'abs\*\(', r'abs(', expr)
            expr = re.sub(r'(\w+)\*\(', r'\1(', expr)

            return expr

        try:
            # Парсим x(t)
            x_parsed = parse_param_expr(self.x_expr)
            self.x_expr_sym = sympify(x_parsed, evaluate=True)
            print(f"✅ x(t) = {self.x_expr_sym}")

            # Парсим y(t)
            y_parsed = parse_param_expr(self.y_expr)
            self.y_expr_sym = sympify(y_parsed, evaluate=True)
            print(f"✅ y(t) = {self.y_expr_sym}")

            # Вычисляем производные dx/dt и dy/dt
            try:
                self.dx_dt_sym = diff(self.x_expr_sym, self.t_sym)
                self.dy_dt_sym = diff(self.y_expr_sym, self.t_sym)
                print(f"✅ dx/dt = {self.dx_dt_sym}")
                print(f"✅ dy/dt = {self.dy_dt_sym}")
            except Exception as e:
                print(f"⚠️ Не удалось вычислить производные: {e}")

        except Exception as e:
            print(f"❌ Ошибка парсинга параметрических выражений: {e}")

    def analyze(self):
        """
        Анализ параметрической кривой.
        """
        return {
            'type': 'parametric',
            'parameter_range': f"t ∈ [{self.x_min:.2f}; {self.x_max:.2f}]",
            'x_range': self._parametric_coord_range('x'),
            'y_range': self._parametric_coord_range('y'),
            'curve_length': self._curve_length(),
            'special_points': self._find_special_parametric_points(),
            'self_intersections': self._find_self_intersections(),
            'curvature_extrema': self._find_curvature_extrema(),
            'curve_type': self._identify_curve_type(),
        }

    def to_text(self):
        """
        Текстовое представление анализа.
        """
        a = self.analyze()

        result = f"Анализ параметрической кривой:\n"
        result += f"   x(t) = {self.x_expr}\n"
        result += f"   y(t) = {self.y_expr}\n\n"
        result += f"• Тип кривой: {a['curve_type']}\n"
        result += f"• Диапазон параметра: {a['parameter_range']}\n"
        result += f"• Диапазон x: {a['x_range']}\n"
        result += f"• Диапазон y: {a['y_range']}\n"
        result += f"• Длина кривой: {a['curve_length']}\n"
        result += f"• Особые точки:\n   {a['special_points']}\n"
        result += f"• Самопересечения: {a['self_intersections']}\n"
        result += f"• Экстремумы кривизны:\n   {a['curvature_extrema']}"
        return result

    def _parametric_coord_range(self, coord='x'):
        """
        Определение диапазона координаты для параметрической кривой.
        """
        try:
            func = self.x_func if coord == 'x' else self.y_func
            ts = np.linspace(self.x_min, self.x_max, 1000)
            vals = []

            for t in ts:
                try:
                    val = func(t)
                    if np.isfinite(val):
                        vals.append(val)
                except:
                    continue

            if not vals:
                return "не определён"

            v_min, v_max = min(vals), max(vals)
            return f"[{v_min:.2f}; {v_max:.2f}]"

        except Exception as e:
            print(f"⚠️ Ошибка определения диапазона {coord}: {e}")
            return "не определён"

    def _curve_length(self):
        """
        Вычисление длины параметрической кривой.
        """
        try:
            ts = np.linspace(self.x_min, self.x_max, 2000)
            length = 0

            for i in range(len(ts) - 1):
                t1, t2 = ts[i], ts[i + 1]

                try:
                    x1, y1 = self.x_func(t1), self.y_func(t1)
                    x2, y2 = self.x_func(t2), self.y_func(t2)

                    if all(np.isfinite([x1, y1, x2, y2])):
                        dx = x2 - x1
                        dy = y2 - y1
                        length += np.sqrt(dx**2 + dy**2)
                except:
                    continue

            return f"L ≈ {length:.2f}"

        except Exception as e:
            print(f"⚠️ Ошибка вычисления длины: {e}")
            return "не определена"

    def _find_special_parametric_points(self):
        """
        Поиск особых точек параметрической кривой.
        """
        special = []

        try:
            # Точки где dx/dt = 0 (вертикальная касательная)
            if self.dx_dt_sym is not None:
                try:
                    t_vertical = solve(self.dx_dt_sym, self.t_sym)
                    for t in t_vertical:
                        if t.is_real or t.is_real is None:
                            t_val = float(t.evalf())
                            if self.x_min <= t_val <= self.x_max:
                                x_val = self.x_func(t_val)
                                y_val = self.y_func(t_val)
                                special.append(f"Вертикальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
                except:
                    pass

            # Точки где dy/dt = 0 (горизонтальная касательная)
            if self.dy_dt_sym is not None:
                try:
                    t_horizontal = solve(self.dy_dt_sym, self.t_sym)
                    for t in t_horizontal:
                        if t.is_real or t.is_real is None:
                            t_val = float(t.evalf())
                            if self.x_min <= t_val <= self.x_max:
                                x_val = self.x_func(t_val)
                                y_val = self.y_func(t_val)
                                special.append(f"Горизонтальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
                except:
                    pass

            # Точки где dx/dt = dy/dt = 0 (особая точка)
            if self.dx_dt_sym is not None and self.dy_dt_sym is not None:
                try:
                    singular = solve([self.dx_dt_sym, self.dy_dt_sym], self.t_sym)
                    for sol in singular:
                        if isinstance(sol, dict):
                            t_val = float(sol[self.t_sym].evalf())
                        else:
                            t_val = float(sol.evalf())

                        if self.x_min <= t_val <= self.x_max:
                            x_val = self.x_func(t_val)
                            y_val = self.y_func(t_val)
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

    def _find_self_intersections(self):
        """
        Поиск самопересечений параметрической кривой.
        """
        try:
            ts = np.linspace(self.x_min, self.x_max, 500)
            points = {}
            intersections = []

            for t in ts:
                try:
                    x = self.x_func(t)
                    y = self.y_func(t)

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

    def _find_curvature_extrema(self):
        """
        Поиск экстремумов кривизны.
        """
        try:
            # κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
            if self.dx_dt_sym is None or self.dy_dt_sym is None:
                return "Не определены"

            # Вторые производные
            d2x_dt2 = diff(self.dx_dt_sym, self.t_sym)
            d2y_dt2 = diff(self.dy_dt_sym, self.t_sym)

            # Численный поиск экстремумов кривизны
            ts = np.linspace(self.x_min, self.x_max, 500)
            curvatures = []

            for t in ts:
                try:
                    dx = float(self.dx_dt_sym.subs(self.t_sym, t))
                    dy = float(self.dy_dt_sym.subs(self.t_sym, t))
                    d2x = float(d2x_dt2.subs(self.t_sym, t))
                    d2y = float(d2y_dt2.subs(self.t_sym, t))

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
                t_min, k_min = curvatures[0]
                x_min, y_min = self.x_func(t_min), self.y_func(t_min)
                result.append(f"Минимум κ={k_min:.3f} при t={t_min:.2f}, ({x_min:.2f}, {y_min:.2f})")

            if len(curvatures) > 1:
                t_max, k_max = curvatures[-1]
                x_max, y_max = self.x_func(t_max), self.y_func(t_max)
                result.append(f"Максимум κ={k_max:.3f} при t={t_max:.2f}, ({x_max:.2f}, {y_max:.2f})")

            return "\n    ".join(result) if result else "Не найдены"

        except Exception as e:
            print(f"⚠️ Ошибка анализа кривизны: {e}")
            return "Не определены"

    def _identify_curve_type(self):
        """
        Определение типа параметрической кривой.
        """
        try:
            # Проверяем на окружность: x² + y² = r²
            if self.x_expr_sym is not None and self.y_expr_sym is not None:
                # Подставляем несколько значений t
                test_t = [0, np.pi/4, np.pi/2, np.pi, 3*np.pi/2]
                radii = []

                for t_val in test_t:
                    try:
                        x = float(self.x_expr_sym.subs(self.t_sym, t_val))
                        y = float(self.y_expr_sym.subs(self.t_sym, t_val))
                        r = np.sqrt(x**2 + y**2)
                        radii.append(r)
                    except:
                        continue

                if radii and max(radii) - min(radii) < 0.1:
                    return f"Окружность (r ≈ {np.mean(radii):.2f})"

            # Проверяем на эллипс: (x/a)² + (y/b)² = 1
            # Ищем паттерн cos(t), sin(t)
            x_str = str(self.x_expr_sym).lower()
            y_str = str(self.y_expr_sym).lower()

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
