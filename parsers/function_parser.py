"""
Парсер для обычных функций вида y = f(x)
"""
import math
from .base_parser import BaseParser


class FunctionParser(BaseParser):
    """
    Парсер для обычных функций y = f(x)
    """
    @staticmethod
    def parse(expr):
        """
        Парсит выражение функции вида y = f(x)
        
        Args:
            expr: строка вида "x**2" или "sin(x)"
        
        Returns:
            func: функция, принимающая x и возвращающая y
        """
        # print(f"\n🔧 ПАРСЕР: Обработка: '{expr}'") # DEBUG

        processed_expr = FunctionParser._preprocess_expression(expr)
        # print(f"🔧 После обработки: '{processed_expr}'") # DEBUG

        # Создаем безопасную функцию, передавая имя переменной 'x'
        safe_func = FunctionParser._create_safe_function(processed_expr, 'x')

        # Тестируем
        # print(f"\n🔧 Тест парсера:") # DEBUG
        test_values = [0, 1.57, 3.14]
        for val in test_values:
            try:
                y = safe_func(val)
                # print(f"  f({val:.2f}) = {y}") # DEBUG
            except Exception as e:
                # print(f"  f({val:.2f}) = ERROR: {e}") # DEBUG
                pass

        return safe_func