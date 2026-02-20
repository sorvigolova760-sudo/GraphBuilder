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
        try:
            safe_func = FunctionParser._create_safe_function(processed_expr, 'x')
        except Exception as e:
            # В случае критической ошибки безопасности — логируем и возвращаем функцию, дающую NaN
            import logging
            logging.getLogger(__name__).warning("Parser rejected expression '%s': %s", expr, e)
            def _nan(*args):
                return float('nan')
            return _nan

        # Тестируем (ошибки внутри safe_func уже обрабатываются и возвращают NaN)
        test_values = [0, 1.57, 3.14]
        for val in test_values:
            try:
                _ = safe_func(val)
            except Exception:
                # на всякий случай — не даем исключение наружу
                pass

        return safe_func