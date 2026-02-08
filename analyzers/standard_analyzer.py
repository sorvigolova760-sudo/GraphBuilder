"""
Анализатор для обычных функций y = f(x)
"""
from .base_analyzer import BaseAnalyzer
from sympy.calculus.util import continuous_domain
from sympy import S, simplify, diff, solve
import numpy as np
import re


class StandardAnalyzer(BaseAnalyzer):
    """
    Анализатор для обычных функций y = f(x)
    """
    def __init__(self, func, user_expr, x_min, x_max):
        super().__init__(func, user_expr, x_min, x_max, func_type='standard')
        self._parse_sympy_expression()

    def analyze(self):
        """
        Полный анализ обычной функции.
        """
        return {
            'type': 'standard',
            'domain': self._analyze_domain(),
            'range': self._analyze_range(),
            'zeros': self._find_zeros(),
            'sign': self._analyze_sign(),
            'extrema': self._find_extrema(),
            'monotonicity': self._analyze_monotonicity(),
            'parity': self._analyze_parity(),
        }

    def to_text(self):
        """
        Текстовое представление анализа.
        """
        a = self.analyze()

        result = f"Анализ функции: f(x) = {self.user_expr}\n\n"
        result += f"• Область определения: {a['domain']}\n"
        result += f"• Множество значений: {a['range']}\n"
        result += f"• Нули функции: {a['zeros']}\n"
        result += f"• Промежутки знакопостоянства:\n   {a['sign']}\n"
        result += f"• Экстремумы:\n   {a['extrema']}\n"
        result += f"• Монотонность:\n   {a['monotonicity']}\n"
        result += f"• Чётность: {a['parity']}"
        return result

    def _analyze_domain(self):
        """
        Анализ области определения.
        """
        if self.expr_sym is None:
            return self._fallback_domain()

        try:
            domain = continuous_domain(self.expr_sym, self.x_sym, S.Reals)

            if domain == S.Reals:
                return "D(f) = R"
            elif domain.is_Interval:
                return f"D(f) = {self._format_interval(domain)}"
            elif domain.is_Union:
                parts = [self._format_interval(i) for i in domain.args]
                return f"D(f) = {' U '.join(parts)}"
            elif domain.is_EmptySet:
                return "D(f) = Ø"
            else:
                return "D(f) = R"

        except Exception as e:
            print(f"⚠️ Ошибка определения области: {e}")
            return self._fallback_domain()

    def _fallback_domain(self):
        """
        Эвристическое определение области.
        """
        expr = self.user_expr.lower()

        if 'log(' in expr or 'ln(' in expr:
            if re.search(r'log\(x\s*[-+]', expr):
                return "D(f) зависит от аргумента логарифма"
            return "D(f) = (0; +∞)"

        if 'sqrt(' in expr:
            if 'sqrt(x)' in expr.replace(' ', ''):
                return "D(f) = [0; +∞)"
            return "D(f) зависит от подкоренного выражения"

        if re.search(r'/\s*x\b', expr) or '1/x' in expr:
            return "D(f) = R \\ {0}"

        if 'asin(' in expr or 'acos(' in expr or 'arcsin(' in expr or 'arccos(' in expr:
            return "D(f) = [−1; 1]"

        return "D(f) = R"

    def _analyze_range(self):
        """
        Анализ множества значений.
        """
        numerical_range = self._numerical_range()
        analytical_range = self._analytical_range()

        if analytical_range:
            return analytical_range

        return numerical_range

    def _numerical_range(self):
        """
        Численное определение множества значений.
        """
        try:
            xs = np.linspace(self.x_min, self.x_max, 2000)
            ys = []

            for x in xs:
                try:
                    y = self.func(x)
                    if np.isfinite(y):
                        ys.append(y)
                except:
                    continue

            if not ys:
                return "E(f) = Ø"

            y_min, y_max = min(ys), max(ys)

            if abs(y_min) > 1e6 or abs(y_max) > 1e6:
                return "E(f) = (−∞; +∞)"

            y_min = round(y_min, 2)
            y_max = round(y_max, 2)

            return f"E(f) ≈ [{y_min}; {y_max}]"

        except Exception as e:
            print(f"⚠️ Ошибка численного анализа области значений: {e}")
            return "E(f) = не определено"

    def _analytical_range(self):
        """
        Аналитическое определение области значений для простых случаев.
        """
        expr = self.user_expr.lower()

        if re.match(r'^[+-]?\d*\.?\d*\*?x\*\*2\s*[+-]?\s*\d*\.?\d*\*?x?\s*[+-]?\s*\d*\.?\d*$', expr.replace(' ', '')):
            if self.expr_sym:
                try:
                    vertex_x = solve(diff(self.expr_sym, self.x_sym), self.x_sym)
                    if vertex_x:
                        vertex_y = float(self.expr_sym.subs(self.x_sym, vertex_x[0]))
                        if 'x**2' in expr or 'x²' in expr:
                            return f"E(f) = [{vertex_y:.2f}; +∞)"
                        else:
                            return f"E(f) = (−∞; {vertex_y:.2f}]"
                except:
                    pass

        if expr in ['sin(x)', 'cos(x)', 'math.sin(x)', 'math.cos(x)']:
            return "E(f) = [-1; 1]"

        return None

    def _find_zeros(self):
        """
        Поиск нулей функции.
        """
        zeros = []

        if self.expr_sym is not None:
            try:
                solutions = solve(self.expr_sym, self.x_sym)

                for sol in solutions:
                    if sol.is_real or sol.is_real is None:
                        try:
                            val = float(sol.evalf())
                            if self.x_min <= val <= self.x_max:
                                zeros.append(val)
                        except (TypeError, ValueError):
                            continue

            except Exception as e:
                print(f"⚠️ Аналитический поиск нулей не удался: {e}")

        if not zeros:
            zeros = self._numerical_zeros()

        zeros = sorted(list(set([round(z, 4) for z in zeros])))

        if zeros:
            return ", ".join([f"x = {z}" for z in zeros])
        else:
            return "Нулей нет на отрезке"

    def _numerical_zeros(self):
        """
        Численный поиск нулей методом перебора с уточнением.
        """
        zeros = []
        step = (self.x_max - self.x_min) / 1000

        for i in range(1000):
            x1 = self.x_min + i * step
            x2 = x1 + step

            try:
                y1 = self.func(x1)
                y2 = self.func(x2)

                if np.isfinite(y1) and np.isfinite(y2):
                    if y1 * y2 < 0:
                        zero = self._bisect(x1, x2)
                        if zero is not None:
                            zeros.append(zero)
                    elif abs(y1) < 1e-6:
                        zeros.append(x1)

            except:
                continue

        return zeros

    def _bisect(self, a, b, tol=1e-6, max_iter=50):
        """
        Метод деления отрезка пополам для уточнения нуля.
        """
        try:
            for _ in range(max_iter):
                c = (a + b) / 2
                fc = self.func(c)

                if abs(fc) < tol or (b - a) / 2 < tol:
                    return c

                fa = self.func(a)
                if fa * fc < 0:
                    b = c
                else:
                    a = c

            return (a + b) / 2
        except:
            return None

    def _analyze_sign(self):
        """
        Анализ знакопостоянства.
        """
        try:
            zeros_str = self._find_zeros()

            zeros_list = []
            if zeros_str != "Нулей нет на отрезке":
                for part in zeros_str.split(','):
                    try:
                        z = float(part.split('=')[1].strip())
                        zeros_list.append(z)
                    except:
                        continue

            points = sorted([self.x_min] + zeros_list + [self.x_max])

            pos_intervals = []
            neg_intervals = []

            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]

                if b - a < 1e-9:
                    continue

                mid = (a + b) / 2

                try:
                    val = self.func(mid)

                    if not np.isfinite(val):
                        continue

                    if val > 1e-9:
                        pos_intervals.append((a, b))
                    elif val < -1e-9:
                        neg_intervals.append((a, b))

                except:
                    continue

            def format_intervals(intervals):
                if not intervals:
                    return "нет"
                parts = []
                for a, b in intervals:
                    left_bracket = '(' if a > self.x_min else '['
                    right_bracket = ')' if b < self.x_max else ']'
                    parts.append(f"{left_bracket}{a:.2f}; {b:.2f}{right_bracket}")
                return ", ".join(parts)

            pos_str = format_intervals(pos_intervals)
            neg_str = format_intervals(neg_intervals)

            return f"f(x) > 0: {pos_str}\n   f(x) < 0: {neg_str}"

        except Exception as e:
            print(f"⚠️ Ошибка анализа знака: {e}")
            return "f(x) > 0: не определено\n   f(x) < 0: не определено"

    def _find_extrema(self):
        """
        Поиск экстремумов (комбинированный метод).
        """
        extrema = []

        if self.derivative_sym is not None:
            extrema = self._analytical_extrema()

        if not extrema:
            extrema = self._numerical_extrema()

        if not extrema:
            return "Не найдены"

        lines = []
        for typ, x, y in sorted(extrema, key=lambda e: e[1])[:5]:
            label = "Максимум" if typ == 'max' else "Минимум"
            lines.append(f"{label} при x ≈ {x:.3f}, f(x) ≈ {y:.3f}")

        return "\n    ".join(lines)

    def _analytical_extrema(self):
        """
        Аналитический поиск через производную.
        """
        extrema = []

        try:
            critical_points = solve(self.derivative_sym, self.x_sym)

            for cp in critical_points:
                if cp.is_real or cp.is_real is None:
                    try:
                        x_val = float(cp.evalf())

                        if not (self.x_min <= x_val <= self.x_max):
                            continue

                        y_val = self.func(x_val)

                        if not np.isfinite(y_val):
                            continue

                        second_deriv = diff(self.derivative_sym, self.x_sym)
                        second_val = float(second_deriv.subs(self.x_sym, cp).evalf())

                        if second_val > 0:
                            extrema.append(('min', x_val, y_val))
                        elif second_val < 0:
                            extrema.append(('max', x_val, y_val))
                        else:
                            eps = 0.001
                            y_left = self.func(x_val - eps)
                            y_right = self.func(x_val + eps)

                            if y_val > y_left and y_val > y_right:
                                extrema.append(('max', x_val, y_val))
                            elif y_val < y_left and y_val < y_right:
                                extrema.append(('min', x_val, y_val))

                    except (TypeError, ValueError):
                        continue

        except Exception as e:
            print(f"⚠️ Аналитический поиск экстремумов не удался: {e}")

        return extrema

    def _numerical_extrema(self):
        """
        Численный поиск экстремумов.
        """
        extrema = []
        step = (self.x_max - self.x_min) / 500

        for i in range(1, 499):
            x0 = self.x_min + (i - 1) * step
            x1 = self.x_min + i * step
            x2 = self.x_min + (i + 1) * step

            try:
                y0 = self.func(x0)
                y1 = self.func(x1)
                y2 = self.func(x2)

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

    def _analyze_monotonicity(self):
        """
        Анализ монотонности функции.
        """
        try:
            if self.derivative_sym is not None:
                return self._analytical_monotonicity()
            else:
                return self._numerical_monotonicity()
        except Exception as e:
            print(f"⚠️ Ошибка анализа монотонности: {e}")
            return "не определена"

    def _analytical_monotonicity(self):
        """
        Аналитический анализ монотонности через производную.
        """
        try:
            critical_points = solve(self.derivative_sym, self.x_sym)

            crit_vals = []
            for cp in critical_points:
                if cp.is_real or cp.is_real is None:
                    try:
                        val = float(cp.evalf())
                        if self.x_min <= val <= self.x_max:
                            crit_vals.append(val)
                    except:
                        continue

            points = sorted([self.x_min] + crit_vals + [self.x_max])

            increasing = []
            decreasing = []

            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                mid = (a + b) / 2

                try:
                    deriv_val = float(self.derivative_sym.subs(self.x_sym, mid).evalf())

                    if deriv_val > 1e-6:
                        increasing.append((a, b))
                    elif deriv_val < -1e-6:
                        decreasing.append((a, b))
                except:
                    continue

            return self._format_monotonicity(increasing, decreasing)

        except Exception as e:
            print(f"⚠️ Аналитическая монотонность не удалась: {e}")
            return self._numerical_monotonicity()

    def _numerical_monotonicity(self):
        """
        Численный анализ монотонности.
        """
        increasing = []
        decreasing = []

        step = (self.x_max - self.x_min) / 100
        current_interval = None
        current_type = None

        for i in range(99):
            x1 = self.x_min + i * step
            x2 = x1 + step

            try:
                y1 = self.func(x1)
                y2 = self.func(x2)

                if not (np.isfinite(y1) and np.isfinite(y2)):
                    if current_interval:
                        if current_type == 'inc':
                            increasing.append(current_interval)
                        else:
                            decreasing.append(current_interval)
                        current_interval = None
                    continue

                if y2 > y1 + 1e-6:
                    interval_type = 'inc'
                elif y2 < y1 - 1e-6:
                    interval_type = 'dec'
                else:
                    continue

                if current_interval is None:
                    current_interval = (x1, x2)
                    current_type = interval_type
                elif current_type == interval_type:
                    current_interval = (current_interval[0], x2)
                else:
                    if current_type == 'inc':
                        increasing.append(current_interval)
                    else:
                        decreasing.append(current_interval)
                    current_interval = (x1, x2)
                    current_type = interval_type

            except:
                continue

        if current_interval:
            if current_type == 'inc':
                increasing.append(current_interval)
            else:
                decreasing.append(current_interval)

        return self._format_monotonicity(increasing, decreasing)

    def _format_monotonicity(self, increasing, decreasing):
        """
        Форматирование результатов монотонности.
        """
        def format_intervals(intervals):
            if not intervals:
                return "нет"
            parts = []
            for a, b in intervals:
                parts.append(f"[{a:.2f}; {b:.2f}]")
            return ", ".join(parts)

        inc_str = format_intervals(increasing)
        dec_str = format_intervals(decreasing)

        return f"Возрастает: {inc_str}\n   Убывает: {dec_str}"

    def _analyze_parity(self):
        """
        Анализ чётности функции.
        """
        if abs(self.x_min + self.x_max) > 1e-6:
            return "общего вида (область несимметрична)"

        if self.expr_sym is not None:
            try:
                expr_minus_x = self.expr_sym.subs(self.x_sym, -self.x_sym)

                if simplify(expr_minus_x - self.expr_sym) == 0:
                    return "чётная"

                if simplify(expr_minus_x + self.expr_sym) == 0:
                    return "нечётная"

            except Exception as e:
                print(f"⚠️ Аналитическая проверка чётности не удалась: {e}")

        test_points = np.linspace(0.1, min(3.0, self.x_max), 10)
        even = True
        odd = True

        for x in test_points:
            if x > self.x_max or -x < self.x_min:
                break

            try:
                fx = self.func(x)
                fmx = self.func(-x)

                if not (np.isfinite(fx) and np.isfinite(fmx)):
                    even = odd = False
                    break

                if abs(fx - fmx) > 1e-4:
                    even = False

                if abs(fx + fmx) > 1e-4:
                    odd = False

            except:
                even = odd = False
                break

        if even:
            return "чётная"
        elif odd:
            return "нечётная"
        else:
            return "общего вида"

    def _format_interval(self, iv):
        """
        Форматирование интервала для вывода.
        """
        if iv == S.Reals:
            return "R"

        left = str(iv.start).replace('oo', '∞').replace('-∞', '−∞')
        right = str(iv.end).replace('oo', '∞')

        lbracket = '[' if not iv.left_open else '('
        rbracket = ']' if not iv.right_open else ')'

        return f"{lbracket}{left}; {right}{rbracket}"
