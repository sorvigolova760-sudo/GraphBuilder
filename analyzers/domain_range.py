"""
Модуль для анализа области определения и области значений функции
"""
import numpy as np
import re
from sympy.calculus.util import continuous_domain
from sympy import S, symbols, sympify, N, diff


def analyze_domain(expr_sym, user_expr):
    """
    Анализ области определения.
    """
    x_sym = symbols('x')  # Добавлено определение x_sym
    if expr_sym is None:
        return _fallback_domain(user_expr)

    try:
        domain = continuous_domain(expr_sym, x_sym, S.Reals)

        if domain == S.Reals:
            return "D(f) = R"
        elif domain.is_Interval:
            return f"D(f) = {_format_interval(domain)}"
        elif domain.is_Union:
            parts = [_format_interval(i) for i in domain.args]
            return f"D(f) = {' U '.join(parts)}"
        elif domain.is_EmptySet:
            return "D(f) = Ø"
        else:
            return "D(f) = R"

    except Exception as e:
        print(f"⚠️ Ошибка определения области: {e}")
        return _fallback_domain(user_expr)


def _fallback_domain(expr):
    """
    Эвристическое определение области.
    """
    expr_lower = expr.lower()

    if 'log(' in expr_lower or 'ln(' in expr_lower:
        if re.search(r'log\(x\s*[-+]', expr_lower):
            return "D(f) зависит от аргумента логарифма"
        return "D(f) = (0; +∞)"

    if 'sqrt(' in expr_lower:
        if 'sqrt(x)' in expr_lower.replace(' ', ''):
            return "D(f) = [0; +∞)"
        return "D(f) зависит от подкоренного выражения"

    if re.search(r'/\s*x\b', expr_lower) or '1/x' in expr_lower:
        return "D(f) = R \\ {0}"

    if 'asin(' in expr_lower or 'acos(' in expr_lower or 'arcsin(' in expr_lower or 'arccos(' in expr_lower:
        return "D(f) = [−1; 1]"

    return "D(f) = R"


def analyze_range(func, expr_sym, user_expr, x_min, x_max):
    """
    Анализ множества значений.
    """
    x_sym = symbols('x')  # Добавлено определение x_sym
    numerical_range = _numerical_range(func, x_min, x_max)
    analytical_range = _analytical_range(expr_sym, user_expr)

    if analytical_range:
        return analytical_range

    return numerical_range


def _numerical_range(func, x_min, x_max):
    """
    Численное определение множества значений.
    """
    try:
        xs = np.linspace(x_min, x_max, 2000)
        ys = []

        for x in xs:
            try:
                y = func(x)
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


def _analytical_range(expr_sym, user_expr):
    """
    Аналитическое определение области значений для простых случаев.
    """
    if expr_sym is None:
        return None

    x_sym = symbols('x')  # Добавлено определение x_sym
    expr_lower = user_expr.lower()

    if re.match(r'^[+-]?\d*\.?\d*\*?x\*\*2\s*[+-]?\s*\d*\.?\d*\*?x?\s*[+-]?\s*\d*\.?\d*$', expr_lower.replace(' ', '')):
        try:
            vertex_x = solve(diff(expr_sym, x_sym), x_sym)
            if vertex_x:
                vertex_y = float(N(expr_sym.subs(x_sym, vertex_x[0])))
                if 'x**2' in expr_lower or 'x²' in expr_lower:
                    return f"E(f) = [{vertex_y:.2f}; +∞)"
                else:
                    return f"E(f) = (−∞; {vertex_y:.2f}]"
        except:
            pass

    if expr_lower in ['sin(x)', 'cos(x)', 'math.sin(x)', 'math.cos(x)']:
        return "E(f) = [−1; 1]"

    return None


def _format_interval(iv):
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

# Добавлен импорт для solve, т.к. он используется в _analytical_range
from sympy import solve