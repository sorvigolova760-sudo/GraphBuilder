"""
Базовый класс для анализаторов функций
"""
import numpy as np
import sympy as sp
import re


class BaseAnalyzer:
    """
    Базовый класс для анализаторов функций.
    Определяет общие методы и интерфейс для анализа.
    """
    def __init__(self, func, user_expr, x_min, x_max, func_type='standard'):
        """
        Args:
            func: функция для анализа
            user_expr: строковое выражение
            x_min, x_max: границы анализа
            func_type: тип функции ('standard' или 'parametric')
        """
        self.func = func
        self.user_expr = user_expr
        self.x_min = x_min
        self.x_max = x_max
        self.func_type = func_type
        self.x_sym = sp.symbols('x')
        self.expr_sym = None
        self.derivative_sym = None

    def analyze(self):
        """
        Абстрактный метод для выполнения анализа.
        Должен быть переопределен в подклассах.
        """
        raise NotImplementedError("Метод analyze должен быть реализован в подклассе")

    def to_text(self):
        """
        Абстрактный метод для получения текстового представления анализа.
        Должен быть переопределен в подклассах.
        """
        raise NotImplementedError("Метод to_text должен быть реализован в подклассе")

    def _parse_sympy_expression(self):
        """
        Конвертирует пользовательское выражение в sympy формат.
        """
        expr = self.user_expr.lower().strip()

        # Заменяем степени
        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')

        # Убираем math. префиксы для sympy
        expr = re.sub(r'math\.', '', expr)

        # Замена функций на sympy версии
        expr = re.sub(r'\b(?:arcsin|asin)\(', 'asin(', expr)
        expr = re.sub(r'\b(?:arccos|acos)\(', 'acos(', expr)
        expr = re.sub(r'\b(?:arctan|atan)\(', 'atan(', expr)
        expr = re.sub(r'\bln\(', 'log(', expr)

        # Неявное умножение
        expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
        expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)

        # Финальная очистка
        expr = re.sub(r'abs\*\(', r'abs(', expr)
        expr = re.sub(r'(\w+)\*\(', r'\1(', expr)

        print(f"🔍 Выражение для sympy: '{expr}'")

        try:
            self.expr_sym = sp.sympify(expr, evaluate=True)
            print(f"✅ Sympy выражение: {self.expr_sym}")

            # Вычисляем производную
            try:
                self.derivative_sym = sp.diff(self.expr_sym, self.x_sym)
                print(f"✅ Производная: {self.derivative_sym}")
            except Exception as e:
                print(f"⚠️ Не удалось вычислить производную: {e}")
                self.derivative_sym = None

        except Exception as e:
            print(f"❌ Ошибка sympify: {e}")
            self.expr_sym = None
            self.derivative_sym = None
