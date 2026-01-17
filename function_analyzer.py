# function_analyzer.py

# =========== ПАТЧ ДЛЯ ANDROID ===========
import sys
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence
collections.Iterable = collections.abc.Iterable

if 'collections' in sys.modules:
    sys.modules['collections'].Mapping = collections.abc.Mapping
    sys.modules['collections'].Sequence = collections.abc.Sequence
# ========================================

import numpy as np
from sympy import symbols, sympify, solve, S, simplify
from sympy.calculus.util import continuous_domain

class FunctionAnalyzer:
    def __init__(self, func, user_expr, x_min, x_max):
        self.func = func
        self.user_expr = user_expr
        self.x_min = x_min
        self.x_max = x_max
        self.x_sym = symbols('x')
        self.expr_sym = None

        # === КОПИЯ ИЗ FunctionParser.parse ===
        expr = user_expr.lower().strip()
        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')
    
        # Замена функций
        import re
        expr = re.sub(r'(?<!math\.)\b(?:arcsin|asin)\(', 'asin(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arccos|acos)\(', 'acos(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arctan|atan)\(', 'atan(', expr)
        expr = re.sub(r'(?<!math\.)\bsin\(', 'sin(', expr)
        expr = re.sub(r'(?<!math\.)\bcos\(', 'cos(', expr)
        expr = re.sub(r'(?<!math\.)\btan\(', 'tan(', expr)
        expr = re.sub(r'(?<!math\.)\bsqrt\(', 'sqrt(', expr)
        expr = re.sub(r'(?<!math\.)\blog\(', 'log(', expr)
        expr = re.sub(r'(?<!math\.)\bexp\(', 'exp(', expr)
        expr = re.sub(r'(?<!math\.)\babs\(', 'abs(', expr)
    
        # Неявное умножение
        expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
        expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
    
        # Финальная очистка
        expr = re.sub(r'abs\*\(', r'abs(', expr)
        # ===================================

        print(f"🔍 Выражение для sympy: '{expr}'")
        try:
            self.expr_sym = sympify(expr, evaluate=True)
            print(f"✅ Успешно: {self.expr_sym}")
        except Exception as e:
            print(f"❌ Ошибка sympify: {e}")
            self.expr_sym = None
    
    def analyze(self):
        return {
            'domain': self._analyze_domain(),
            'range': self._analyze_range(),
            'zeros': self._find_zeros(),
            'sign': self._analyze_sign(),
            'extrema': self._find_extrema(),
            'parity': self._analyze_parity(),
        }

    def to_text(self):
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
            return "D(f) = R"
        try:
            domain = continuous_domain(self.expr_sym, self.x_sym, S.Reals)
            if domain == S.Reals:
                return "D(f) = R"
            elif domain.is_Interval:
                return f"D(f) = {self._format_interval(domain)}"
            elif domain.is_Union:
                parts = [self._format_interval(i) for i in domain.args]
                return f"D(f) = {' ∪ '.join(parts)}"
            else:
                return "D(f) = R"
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
        zeros = []
        if self.expr_sym is not None:
            try:
                sol = solve(self.expr_sym, self.x_sym)
                for z in sol:
                    if z.is_real:
                        val = float(z.evalf())
                        # Добавляем даже если на границе
                        if self.x_min <= val <= self.x_max:
                            zeros.append(round(val, 6))
            except Exception as e:
                print(f"⚠️ Ошибка при поиске нулей: {e}")

        # Убираем дубликаты и сортируем
        zeros = sorted(set(zeros))
        if zeros:
            return ", ".join([f"x = {z}" for z in zeros])
        else:
            return "Нулей нет на отрезке"

    def _analyze_sign(self):
        try:
            # Получаем нули
            zeros_str = self._find_zeros()
            if zeros_str == "Нулей нет на отрезке":
                # Проверяем знак в одной точке
                test_x = (self.x_min + self.x_max) / 2
                try:
                    val = self.func(test_x)
                    if val > 0:
                        return f"f(x) > 0: [{self.x_min:.2f}; {self.x_max:.2f}]\n   f(x) < 0: нет"
                    else:
                        return f"f(x) > 0: нет\n   f(x) < 0: [{self.x_min:.2f}; {self.x_max:.2f}]"
                except:
                    return "f(x) > 0: не определено\n   f(x) < 0: не определено"

            # Извлекаем числа из строки "x = -4, x = 0, ..."
            zeros_list = []
            for part in zeros_str.split(','):
                try:
                    z = float(part.split('=')[1].strip())
                    zeros_list.append(z)
                except:
                    continue

            if not zeros_list:
                return "f(x) > 0: не определено\n   f(x) < 0: не определено"

            # Сортируем и добавляем границы
            points = sorted([self.x_min] + zeros_list + [self.x_max])
            pos_intervals = []
            neg_intervals = []

            for i in range(len(points) - 1):
                a = points[i]
                b = points[i+1]
                if b - a < 1e-6:
                    continue
                # Берём середину интервала
                mid = (a + b) / 2
                if mid < self.x_min or mid > self.x_max:
                    continue
                try:
                    val = self.func(mid)
                    if val > 0:
                        pos_intervals.append((a, b))
                    elif val < 0:
                        neg_intervals.append((a, b))
                except:
                    continue

            def format_intervals(intervals):
                if not intervals:
                    return "нет"
                parts = []
                for a, b in intervals:
                    parts.append(f"({a:.2f}; {b:.2f})")
                return ", ".join(parts)

            return f"f(x) > 0: {format_intervals(pos_intervals)}\n   f(x) < 0: {format_intervals(neg_intervals)}"

        except Exception:
            return "f(x) > 0: не определено\n   f(x) < 0: не определено"

    def _find_extrema(self):
        # Численный поиск экстремумов
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
        # Проверяем только если область симметрична
        if self.x_min != -self.x_max:
            return "общего вида"
        try:
            test_points = [0.5, 1.0, 1.5, 2.0]
            even = odd = True
            for x in test_points:
                if x > self.x_max:
                    break
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