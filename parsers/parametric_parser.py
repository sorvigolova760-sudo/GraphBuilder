"""
Парсер для параметрических функций вида:
x = x(t)
y = y(t)
"""
from .base_parser import BaseParser


class ParametricParser(BaseParser):
    """
    Парсер для параметрических функций вида:
    x = x(t)
    y = y(t)
    Примеры:
    - Окружность: x = cos(t), y = sin(t)
    - Спираль: x = t*cos(t), y = t*sin(t)
    - Циклоида: x = t - sin(t), y = 1 - cos(t)
    - Эллипс: x = 3*cos(t), y = 2*sin(t)
    """

    @staticmethod
    def parse(x_expr, y_expr):
        """
        Парсит параметрические выражения x(t) и y(t)

        Args:
            x_expr: строка вида "cos(t)" или "t*cos(t)"
            y_expr: строка вида "sin(t)" или "t*sin(t)"

        Returns:
            (x_func, y_func): кортеж функций
        """
        print(f"\n🔧 ПАРАМЕТРИЧЕСКИЙ ПАРСЕР")
        print(f"   x(t) = {x_expr}")
        print(f"   y(t) = {y_expr}")

        x_func = ParametricParser._parse_single(x_expr, 't', 'x')
        y_func = ParametricParser._parse_single(y_expr, 't', 'y')

        # Тестируем
        print(f"\n🔧 Тест параметрического парсера:")
        test_values = [0, 1.57, 3.14, 4.71]  # 0, π/2, π, 3π/2
        for val in test_values:
            x_val = x_func(val)
            y_val = y_func(val)
            print(f"  t={val:.2f}: x={x_val:.3f}, y={y_val:.3f}")

        return x_func, y_func

    @staticmethod
    def _parse_single(expr, param='t', coord='x'):
        """
        Парсит одно параметрическое выражение

        Args:
            expr: строковое выражение
            param: имя параметра (обычно 't')
            coord: название координаты для отладки
        """
        print(f"\n🔧 Парсинг {coord}({param}): '{expr}'")

        processed_expr = ParametricParser._preprocess_expression(expr)
        print(f"🔧 Финальное выражение: '{processed_expr}'")

        # Создаем безопасную функцию, передавая имя параметра
        safe_func = ParametricParser._create_safe_function(processed_expr, param)

        return safe_func