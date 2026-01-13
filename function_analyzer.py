# function_analyzer.py

# =========== ПАТЧ ДЛЯ ANDROID ===========
import sys
import collections
import collections.abc

# Применяем патч ДО импорта sympy
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence
collections.Iterable = collections.abc.Iterable

if 'collections' in sys.modules:
    sys.modules['collections'].Mapping = collections.abc.Mapping
    sys.modules['collections'].Sequence = collections.abc.Sequence
# ========================================
import math
import numpy as np

from sympy import symbols, sympify, diff, solve, S, oo, Interval, Union, limit, simplify
from sympy.calculus.util import continuous_domain, function_range
from sympy.calculus.util import periodicity

class FunctionAnalyzer:
    def __init__(self, func, user_expr, x_min, x_max):
        """
        Анализ функции.
        :param func: численная функция f(x) -> float
        :param user_expr: исходная строка от пользователя (например, "x**2")
        :param x_min, x_max: диапазон для численного анализа
        """
        self.func = func
        self.user_expr = user_expr
        self.x_min = x_min
        self.x_max = x_max
        self.x_sym = symbols('x')
        self.expr_sym = None

        # Очищаем выражение для sympy
        clean_expr = user_expr.replace('math.', '').replace(' ', '')
        try:
            self.expr_sym = sympify(clean_expr)
        except Exception:
            self.expr_sym = None

    def analyze(self):
        """Возвращает словарь с анализом."""
        return {
            'domain': self._analyze_domain(),
            'range': self._analyze_range(),
            'zeros': self._find_zeros(),
            'sign': self._analyze_sign(),
            'extrema': self._find_extrema(),
            'parity': self._analyze_parity(),
        }

    def to_text(self):
        """Форматирует анализ в читаемый текст."""
        a = self.analyze()
        return f"""\
Анализ функции: f(x) = {self.user_expr}

• Область определения: {a['domain']}
• Множество значений: {a['range']}
• Нули функции: {a['zeros']}
• Промежутки знакопостоянства:
   {a['sign']}
• Экстремумы:
   {a['extrema']}
• Чётность: {a['parity']}"""

    def _analyze_domain(self):
        if self.expr_sym is None:
            return "Не удалось определить"
        try:
            domain = continuous_domain(self.expr_sym, self.x_sym, S.Reals)
            if domain == S.Reals:
                return "D(f) = R"
            elif domain.is_Interval:
                return f"D(f) = {self._format_interval(domain)}"
            elif domain.is_Union:
                parts = [self._format_interval(i) for i in domain.args]
                return f"D(f) = {' U '.join(parts)}"
            else:
                return "D(f) = R (предположительно)"
        except Exception:
            return self._fallback_domain()

    def _fallback_domain(self):
        expr = self.user_expr.lower()
        if 'log' in expr or 'ln' in expr:
            return "D(f) = (0; +∞)"
        elif 'sqrt' in expr or '**0.5' in expr:
            return "D(f) = [0; +∞)"
        elif '/x' in expr or '1/x' in expr:
            return "D(f) = R \\ {{0}}"
        return "D(f) = R"

    def _analyze_range(self):
        if self.expr_sym is not None:
            try:
                rng = function_range(self.expr_sym, self.x_sym, S.Reals)
                if rng == S.Reals:
                    return "E(f) = R"
                elif rng.is_Interval:
                    return f"E(f) = {self._format_interval(rng)}"
                elif rng.is_Union:
                    parts = [self._format_interval(i) for i in rng.args]
                    return f"E(f) = {' U '.join(parts)}"
            except Exception:
                pass

        # Численный резерв
        try:
            xs = np.linspace(self.x_min, self.x_max, 1000)
            ys = []
            for x in xs:
                try:
                    y = self.func(x)
                    if np.isfinite(y):
                        ys.append(y)
                except:
                    continue
            if not ys:
                return "E(f) = ∅"
            y_min, y_max = min(ys), max(ys)
            if abs(y_min) > 1e5 or abs(y_max) > 1e5:
                return "E(f) = (−∞; +∞)"
            return f"E(f) ≈ [{y_min:.2f}; {y_max:.2f}]"
        except Exception:
            return "E(f) = не определено"

    def _find_zeros(self):
        if self.expr_sym is not None:
            try:
                zeros = solve(self.expr_sym, self.x_sym)
                real_zeros = []
                for z in zeros:
                    try:
                        z_val = complex(z.evalf())
                        if abs(z_val.imag) < 1e-8:
                            x = float(z_val.real)
                            if self.x_min <= x <= self.x_max:
                                real_zeros.append(round(x, 4))
                    except:
                        continue
                if real_zeros:
                    real_zeros = sorted(set(real_zeros))
                    return ", ".join([f"x = {z}" for z in real_zeros])
            except Exception:
                pass

        # Численный поиск
        try:
            zeros = []
            step = (self.x_max - self.x_min) / 200
            for i in range(200):
                x1 = self.x_min + i * step
                x2 = x1 + step
                try:
                    y1, y2 = self.func(x1), self.func(x2)
                    if y1 == 0:
                        zeros.append(x1)
                    elif y1 * y2 < 0:
                        root = self._bisection(x1, x2)
                        if root and self.x_min <= root <= self.x_max:
                            zeros.append(root)
                except:
                    continue
            unique = sorted(set(round(z, 3) for z in zeros))
            if unique:
                return ", ".join([f"x ≈ {z}" for z in unique])
            return "Нулей нет на отрезке"
        except Exception:
            return "Не найдены"

    def _bisection(self, a, b, tol=1e-6, max_iter=50):
        try:
            fa, fb = self.func(a), self.func(b)
            if fa * fb > 0:
                return None
            for _ in range(max_iter):
                c = (a + b) / 2
                fc = self.func(c)
                if abs(fc) < tol:
                    return c
                if fa * fc < 0:
                    b, fb = c, fc
                else:
                    a, fa = c, fc
            return (a + b) / 2
        except Exception:
            return None

    def _analyze_sign(self):
        try:
            pos, neg = [], []
            step = (self.x_max - self.x_min) / 100
            points = [self.x_min + i * step for i in range(101)]
            intervals = []

            for i in range(len(points) - 1):
                mid = (points[i] + points[i+1]) / 2
                try:
                    y = self.func(mid)
                    if y > 0:
                        intervals.append(('pos', points[i], points[i+1]))
                    elif y < 0:
                        intervals.append(('neg', points[i], points[i+1]))
                except:
                    continue

            # Объединяем соседние интервалы
            if intervals:
                current_type, start, end = intervals[0]
                for typ, a, b in intervals[1:]:
                    if typ == current_type and abs(a - end) < step * 1.1:
                        end = b
                    else:
                        if current_type == 'pos':
                            pos.append((start, end))
                        else:
                            neg.append((start, end))
                        current_type, start, end = typ, a, b
                if current_type == 'pos':
                    pos.append((start, end))
                else:
                    neg.append((start, end))

            pos_str = self._format_intervals(pos) or "нет"
            neg_str = self._format_intervals(neg) or "нет"
            return f"f(x) > 0: {pos_str}\n   f(x) < 0: {neg_str}"
        except Exception:
            return "f(x) > 0: не определено\n   f(x) < 0: не определено"

    def _find_extrema(self):
        if self.expr_sym is not None:
            try:
                f_prime = diff(self.expr_sym, self.x_sym)
                crit_points = solve(f_prime, self.x_sym)
                extrema = []
                for cp in crit_points:
                    try:
                        x_val = float(cp.evalf())
                        if self.x_min <= x_val <= self.x_max:
                            y_val = self.func(x_val)
                            # Проверка окрестности
                            left = self.func(x_val - 1e-4)
                            right = self.func(x_val + 1e-4)
                            if y_val > left and y_val > right:
                                extrema.append(('max', x_val, y_val))
                            elif y_val < left and y_val < right:
                                extrema.append(('min', x_val, y_val))
                    except:
                        continue
                if extrema:
                    lines = []
                    for typ, x, y in sorted(extrema, key=lambda e: e[1])[:3]:
                        lines.append(f"{'Максимум' if typ == 'max' else 'Минимум'} при x = {x:.3f}, f(x) = {y:.3f}")
                    return "\n   ".join(lines)
            except Exception:
                pass

        # Численный резерв
        try:
            extrema = []
            step = (self.x_max - self.x_min) / 300
            for i in range(1, 299):
                x0 = self.x_min + (i-1)*step
                x1 = self.x_min + i*step
                x2 = self.x_min + (i+1)*step
                try:
                    y0, y1, y2 = self.func(x0), self.func(x1), self.func(x2)
                    if np.isfinite(y0) and np.isfinite(y1) and np.isfinite(y2):
                        if y1 > y0 and y1 > y2:
                            extrema.append(('max', x1, y1))
                        elif y1 < y0 and y1 < y2:
                            extrema.append(('min', x1, y1))
                except:
                    continue
            if extrema:
                lines = []
                for typ, x, y in sorted(extrema, key=lambda e: e[1])[:3]:
                    lines.append(f"{'Максимум' if typ == 'max' else 'Минимум'} при x ≈ {x:.3f}, f(x) ≈ {y:.3f}")
                return "\n   ".join(lines)
            return "Не найдены"
        except Exception:
            return "Не найдены"

    def _analyze_parity(self):
        try:
            test_points = [0.5, 1.0, 1.5, 2.0]
            even = odd = True
            for x in test_points:
                try:
                    fx = self.func(x)
                    fmx = self.func(-x)
                    if not (np.isfinite(fx) and np.isfinite(fmx)):
                        even = odd = False
                        break
                    if abs(fx - fmx) > 1e-6:
                        even = False
                    if abs(fx + fmx) > 1e-6:
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
        except Exception:
            return "не определена"

    def _format_interval(self, iv):
        if iv == S.Reals:
            return "R"
        left = str(iv.start).replace('oo', '∞')
        right = str(iv.end).replace('oo', '∞')
        lbracket = '[' if iv.left_open == False else '('
        rbracket = ']' if iv.right_open == False else ')'
        return f"{lbracket}{left}; {right}{rbracket}"

    def _format_intervals(self, intervals):
        if not intervals:
            return ""
        parts = []
        for a, b in intervals:
            if b - a < 0.01:
                continue
            parts.append(f"[{a:.2f}; {b:.2f}]")
        return ", ".join(parts)