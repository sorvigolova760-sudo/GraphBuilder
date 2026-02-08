"""
Базовый класс для парсеров функций
"""
import math
import re


class BaseParser:
    """
    Базовый класс для парсеров математических выражений.
    Содержит общие методы для обработки выражений.
    """
    @staticmethod
    def _preprocess_expression(expr):
        """
        Предварительная обработка выражения: замена степеней, функций и т.д.
        """
        if not isinstance(expr, str):
             raise TypeError(f"Выражение должно быть строкой, получено: {type(expr)}")
        expr = expr.lower().strip()

        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')

        # ЗАМЕНА ФУНКЦИЙ
        replacements = [
            (r'(?<!math\.)\b(?:arcsin|asin)\(', lambda m: 'math.asin('),
            (r'(?<!math\.)\b(?:arccos|acos)\(', lambda m: 'math.acos('),
            (r'(?<!math\.)\b(?:arctan|atan)\(', lambda m: 'math.atan('),
            (r'(?<!math\.)\b(?:cot|ctg)\(', lambda m: '1/math.tan('),
            (r'(?<!math\.)\bsin\(', lambda m: 'math.sin('),
            (r'(?<!math\.)\bcos\(', lambda m: 'math.cos('),
            (r'(?<!math\.)\btan\(', lambda m: 'math.tan('),
            (r'(?<!math\.)\bsqrt\(', lambda m: 'math.sqrt('),
            (r'(?<!math\.)\blog\(', lambda m: 'math.log('),
            (r'(?<!math\.)\bln\(', lambda m: 'math.log('),
            (r'(?<!math\.)\bexp\(', lambda m: 'math.exp('),
            (r'(?<!math\.)\babs\(', lambda m: 'abs('),
        ]

        for pattern, repl_func in replacements:
            expr = re.sub(pattern, repl_func, expr)

        # Неявное умножение
        mult_replacements = [
            (r'(\d)(?![.\d])([a-zA-Z])', lambda m: f'{m.group(1)}*{m.group(2)}'),
            (r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*('),
            (r'(\))([a-zA-Z\d])', lambda m: f'{m.group(1)}*{m.group(2)}'),
            (r'([a-zA-Z])(\d)', lambda m: f'{m.group(1)}*{m.group(2)}'),
        ]

        for pattern, repl_func in mult_replacements:
            if callable(repl_func):
                expr = re.sub(pattern, repl_func, expr)
            else:
                expr = re.sub(pattern, repl_func, expr)

        # Финальная очистка
        cleanup_replacements = [
            (r'math\.(\w+)\*\(', lambda m: f'math.{m.group(1)}('),
            (r'abs\*\(', lambda m: 'abs('),
        ]

        for pattern, repl_func in cleanup_replacements:
            expr = re.sub(pattern, repl_func, expr)

        return expr

    @staticmethod
    def _create_safe_function(expr, var_name='x'): # Добавлен аргумент var_name
        """
        Создание безопасной функции для вычисления выражения.
        var_name - имя переменной (например, 'x' для f(x) или 't' для x(t), y(t))
        """
        def func(*args):
            try:
                # args[0] - это значение переменной (x или t)
                var_val = args[0]
                context = {
                    'math': math,
                    'pi': math.pi,
                    'e': math.e,
                    var_name: var_val, # Передаем переменную с правильным именем
                }
                # print(f"DEBUG: eval expr='{expr}', context keys={list(context.keys())}") # DEBUG
                result = eval(expr, {"__builtins__": {}}, context)

                if isinstance(result, (int, float)):
                    return float(result)
                else:
                    return float('nan')

            except ZeroDivisionError:
                return float('inf')
            except (ValueError, TypeError, NameError, SyntaxError, AttributeError) as e:
                # print(f"DEBUG: Error in eval: {e}") # DEBUG
                return float('nan')

        return func