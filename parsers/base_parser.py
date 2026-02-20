"""
Базовый класс для парсеров функций
"""
import math
import re
import ast
import logging

logger = logging.getLogger(__name__)


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
        # AST-based safety check: разбор и валидация узлов
        def _is_ast_safe(expression, var_name):
            try:
                node = ast.parse(expression, mode='eval')
            except Exception as e:
                logger.debug("AST parse failed: %s", e)
                return False

            allowed_funcs = {'sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sqrt', 'log', 'exp', 'abs'}
            allowed_names = {'math', 'pi', 'e', var_name}

            class SafetyVisitor(ast.NodeVisitor):
                def visit_Attribute(self, node):
                    # allow only math.<func>
                    if isinstance(node.value, ast.Name) and node.value.id == 'math' and isinstance(node.attr, str):
                        if node.attr in allowed_funcs:
                            return self.generic_visit(node)
                    raise ValueError(f"Attribute access not allowed: {ast.dump(node)}")

                def visit_Call(self, node):
                    # Calls allowed if function is Name (like abs) or math.<func>
                    if isinstance(node.func, ast.Name):
                        if node.func.id not in allowed_funcs and node.func.id not in allowed_names:
                            raise ValueError(f"Call to disallowed function: {node.func.id}")
                    elif isinstance(node.func, ast.Attribute):
                        # will be checked in visit_Attribute
                        pass
                    else:
                        raise ValueError(f"Disallowed call node: {ast.dump(node.func)}")
                    for arg in node.args:
                        self.visit(arg)

                def visit_Name(self, node):
                    if node.id not in allowed_names and node.id not in allowed_funcs:
                        raise ValueError(f"Use of unknown name: {node.id}")

                def visit_Subscript(self, node):
                    raise ValueError("Subscript access not allowed")

                def visit_Import(self, node):
                    raise ValueError("Import not allowed")

                def visit_ImportFrom(self, node):
                    raise ValueError("ImportFrom not allowed")

                def visit_Lambda(self, node):
                    raise ValueError("Lambda not allowed")

                def visit_FunctionDef(self, node):
                    raise ValueError("Function definitions not allowed")

                def visit_ClassDef(self, node):
                    raise ValueError("Class definitions not allowed")

            try:
                SafetyVisitor().visit(node)
                return True
            except Exception as e:
                logger.warning("AST safety check failed for '%s': %s", expression, e)
                return False

        if not _is_ast_safe(expr, var_name):
            logger.warning("Expression failed AST safety check: %s", expr)

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
                logger.debug("Error evaluating expression '%s': %s", expr, e)
                return float('nan')

        return func