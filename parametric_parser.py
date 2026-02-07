# parametric_parser.py
import math
import re

class ParametricParser:
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
        
        original = expr
        expr = expr.lower().strip()
        
        # Заменяем степени
        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')
        
        # ЗАМЕНА ФУНКЦИЙ с защитой от повторной замены
        expr = re.sub(r'(?<!math\.)\b(?:arcsin|asin)\(', 'math.asin(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arccos|acos)\(', 'math.acos(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:arctan|atan)\(', 'math.atan(', expr)
        expr = re.sub(r'(?<!math\.)\b(?:cot|ctg)\(', '1/math.tan(', expr)
        expr = re.sub(r'(?<!math\.)\bsin\(', 'math.sin(', expr)
        expr = re.sub(r'(?<!math\.)\bcos\(', 'math.cos(', expr)
        expr = re.sub(r'(?<!math\.)\btan\(', 'math.tan(', expr)
        expr = re.sub(r'(?<!math\.)\bsqrt\(', 'math.sqrt(', expr)
        expr = re.sub(r'(?<!math\.)\blog\(', 'math.log(', expr)
        expr = re.sub(r'(?<!math\.)\bln\(', 'math.log(', expr)
        expr = re.sub(r'(?<!math\.)\bexp\(', 'math.exp(', expr)
        expr = re.sub(r'(?<!math\.)\babs\(', 'abs(', expr)
        
        print(f"🔧 После замен функций: '{expr}'")
        
        # Неявное умножение (параметр обычно 't')
        expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
        expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
        expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        
        print(f"🔧 После умножения: '{expr}'")
        
        # Финальная очистка
        expr = re.sub(r'math\.(\w+)\*\(', r'math.\1(', expr)
        expr = re.sub(r'abs\*\(', r'abs(', expr)
        
        print(f"🔧 Финальное выражение: '{expr}'")
        
        # Создаем безопасную функцию
        def func(t):
            try:
                context = {
                    'math': math,
                    't': t,
                    'pi': math.pi,
                    'e': math.e,
                    'sin': math.sin,
                    'cos': math.cos,
                    'tan': math.tan,
                    'tg': math.tan,
                    'tag': math.tan,
                    'asin': math.asin,
                    'acos': math.acos,
                    'atan': math.atan,
                    'cot': lambda x: 1 / math.tan(x),  # котангенс
                    'ctg': lambda x: 1 / math.tan(x),  # котангенс (русская версия)
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
                return float('inf') if t > 0 else float('-inf')
            except (ValueError, TypeError, NameError, SyntaxError, AttributeError) as e:
                print(f"⚠️ Ошибка вычисления {coord}({t}): {e}")
                return float('nan')
        
        return func


# ========== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ==========

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ПРИМЕРЫ ПАРАМЕТРИЧЕСКИХ КРИВЫХ")
    print("="*60)
    
    # Пример 1: Окружность
    print("\n1. ОКРУЖНОСТЬ: x = cos(t), y = sin(t)")
    x_func, y_func = ParametricParser.parse("cos(t)", "sin(t)")
    
    # Пример 2: Эллипс
    print("\n2. ЭЛЛИПС: x = 3*cos(t), y = 2*sin(t)")
    x_func, y_func = ParametricParser.parse("3*cos(t)", "2*sin(t)")
    
    # Пример 3: Спираль Архимеда
    print("\n3. СПИРАЛЬ: x = t*cos(t), y = t*sin(t)")
    x_func, y_func = ParametricParser.parse("t*cos(t)", "t*sin(t)")
    
    # Пример 4: Циклоида
    print("\n4. ЦИКЛОИДА: x = t - sin(t), y = 1 - cos(t)")
    x_func, y_func = ParametricParser.parse("t - sin(t)", "1 - cos(t)")
    
    # Пример 5: Лемниската Бернулли
    print("\n5. ФИГУРА ЛИССАЖУ: x = sin(2*t), y = sin(3*t)")
    x_func, y_func = ParametricParser.parse("sin(2*t)", "sin(3*t)")
    
    print("\n" + "="*60)
    print("✅ Все примеры успешно распарсены!")
    print("="*60)