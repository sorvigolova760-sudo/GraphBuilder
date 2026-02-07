# function_parser.py
import math
import re

class FunctionParser:
    """Окончательный исправленный парсер"""
    
    @staticmethod
    def parse(expr):
        print(f"\n🔧 ПАРСЕР: Обработка: '{expr}'")
        original = expr
        expr = expr.lower().strip()
        
        # 3. Заменяем степени
        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')
        
        # 4. ЗАМЕНА ФУНКЦИЙ с защитой от повторной замены внутри math.
        expr = re.sub(r'(?<!math\.)\b(?:arcsin|asin)\(', 'math.asin(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arccos|acos)\(', 'math.acos(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arctan|atan)\(', 'math.atan(', expr)
        expr = re.sub(r'(?<!math\.)\bsin\(', 'math.sin(', expr)
        expr = re.sub(r'(?<!math\.)\bcos\(', 'math.cos(', expr)
        expr = re.sub(r'(?<!math\.)\btan\(', 'math.tan(', expr)
        expr = re.sub(r'(?<!math\.)\bsqrt\(', 'math.sqrt(', expr)
        expr = re.sub(r'(?<!math\.)\blog\(', 'math.log(', expr)
        expr = re.sub(r'(?<!math\.)\bexp\(', 'math.exp(', expr)
        expr = re.sub(r'(?<!math\.)\babs\(', 'abs(', expr)
        
        print(f"🔧 После замен функций: '{expr}'")
        
        # 5. Неявное умножение
        expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
        expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        
        print(f"🔧 После умножения: '{expr}'")
        
        # 6. Финальная очистка
        expr = re.sub(r'math\.(\w+)\*\(', r'math.\1(', expr)
        expr = re.sub(r'abs\*\(', r'abs(', expr)
        
        print(f"🔧 Финальное выражение: '{expr}'")
        
        # 7. Создаем безопасную функцию
        def func(x):
            try:
                context = {
                    'math': math,
                    'x': x,
                    'pi': math.pi,
                    'e': math.e,
                    'sin': math.sin,
                    'cos': math.cos,
                    'tg': math.tan,
                    'tag': math.tan,
                    'tan': math.tan,
                    'asin': math.asin,
                    'acos': math.acos,
                    'atan': math.atan,
                    'sqrt': math.sqrt,
                    'log': math.log,
                    'exp': math.exp,
                    'abs': abs,
                }
                result = eval(expr, {"__builtins__": {}}, context)
                if isinstance(result, (int, float)):
                    return float(result)
                else:
                    return float('nan')
            except ZeroDivisionError:
                return float('inf') if x > 0 else float('-inf')
            except (ValueError, TypeError, NameError, SyntaxError, AttributeError):
                return float('nan')
        
        # 8. Быстрый тест
        print("🔧 Тест парсера:")
        test_values = [0, 1.57, 3.14]
        for val in test_values:
            y = func(val)
            print(f"  f({val:.2f}) = {y}")
        
        return func