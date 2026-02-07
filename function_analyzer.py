# function_analyzer.py (с поддержкой параметрических функций)

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
from sympy import symbols, sympify, solve, S, simplify, diff, limit, oo, sqrt as sym_sqrt
from sympy.calculus.util import continuous_domain
import re

class FunctionAnalyzer:
    """
    Анализатор функций с поддержкой:
    - Обычных функций y = f(x)
    - Параметрических кривых x = x(t), y = y(t)
    """
    
    def __init__(self, func, user_expr, x_min, x_max, func_type='standard', 
                 x_func=None, y_func=None, x_expr=None, y_expr=None):
        """
        Args:
            func: функция для обычных графиков
            user_expr: строковое выражение
            x_min, x_max: границы
            func_type: 'standard' или 'parametric'
            x_func, y_func: функции для параметрических кривых
            x_expr, y_expr: строковые выражения для x(t) и y(t)
        """
        self.func = func
        self.user_expr = user_expr
        self.x_min = x_min
        self.x_max = x_max
        self.func_type = func_type
        
        # Для параметрических функций
        self.x_func = x_func
        self.y_func = y_func
        self.x_expr = x_expr
        self.y_expr = y_expr
        
        # Символы
        self.x_sym = symbols('x')
        self.t_sym = symbols('t')
        
        self.expr_sym = None
        self.derivative_sym = None
        
        # Для параметрических
        self.x_expr_sym = None
        self.y_expr_sym = None
        self.dx_dt_sym = None
        self.dy_dt_sym = None

        # Парсим выражения
        if func_type == 'standard':
            self._parse_sympy_expression()
        elif func_type == 'parametric':
            self._parse_parametric_expressions()
    
    def _parse_sympy_expression(self):
        """Конвертирует пользовательское выражение в sympy формат"""
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
            self.expr_sym = sympify(expr, evaluate=True)
            print(f"✅ Sympy выражение: {self.expr_sym}")
            
            # Вычисляем производную
            try:
                self.derivative_sym = diff(self.expr_sym, self.x_sym)
                print(f"✅ Производная: {self.derivative_sym}")
            except Exception as e:
                print(f"⚠️ Не удалось вычислить производную: {e}")
                self.derivative_sym = None
                
        except Exception as e:
            print(f"❌ Ошибка sympify: {e}")
            self.expr_sym = None
            self.derivative_sym = None
    
    def _parse_parametric_expressions(self):
        """Парсинг параметрических выражений x(t) и y(t)"""
        print(f"\n🔧 ПАРАМЕТРИЧЕСКИЙ РЕЖИМ")
        print(f"   x(t) = {self.x_expr}")
        print(f"   y(t) = {self.y_expr}")
        
        def parse_param_expr(expr_str):
            """Парсинг одного параметрического выражения"""
            expr = expr_str.lower().strip()
            
            # Заменяем степени
            expr = expr.replace('^', '**')
            expr = expr.replace('²', '**2')
            expr = expr.replace('³', '**3')
            
            # Убираем math. префиксы
            expr = re.sub(r'math\.', '', expr)
            
            # Замена функций
            expr = re.sub(r'\b(?:arcsin|asin)\(', 'asin(', expr)
            expr = re.sub(r'\b(?:arccos|acos)\(', 'acos(', expr)
            expr = re.sub(r'\b(?:arctan|atan)\(', 'atan(', expr)
            expr = re.sub(r'\bln\(', 'log(', expr)
            
            # Неявное умножение (заменяем x на t)
            expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
            expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
            expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
            expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
            
            # Финальная очистка
            expr = re.sub(r'abs\*\(', r'abs(', expr)
            expr = re.sub(r'(\w+)\*\(', r'\1(', expr)
            
            return expr
        
        try:
            # Парсим x(t)
            x_parsed = parse_param_expr(self.x_expr)
            self.x_expr_sym = sympify(x_parsed, evaluate=True)
            print(f"✅ x(t) = {self.x_expr_sym}")
            
            # Парсим y(t)
            y_parsed = parse_param_expr(self.y_expr)
            self.y_expr_sym = sympify(y_parsed, evaluate=True)
            print(f"✅ y(t) = {self.y_expr_sym}")
            
            # Вычисляем производные dx/dt и dy/dt
            try:
                self.dx_dt_sym = diff(self.x_expr_sym, self.t_sym)
                self.dy_dt_sym = diff(self.y_expr_sym, self.t_sym)
                print(f"✅ dx/dt = {self.dx_dt_sym}")
                print(f"✅ dy/dt = {self.dy_dt_sym}")
            except Exception as e:
                print(f"⚠️ Не удалось вычислить производные: {e}")
                
        except Exception as e:
            print(f"❌ Ошибка парсинга параметрических выражений: {e}")
    
    def analyze(self):
        """Полный анализ функции"""
        if self.func_type == 'standard':
            return self._analyze_standard()
        elif self.func_type == 'parametric':
            return self._analyze_parametric()
    
    def _analyze_standard(self):
        """Анализ обычной функции y = f(x)"""
        return {
            'type': 'standard',
            'domain': self._analyze_domain(),
            'range': self._analyze_range(),
            'zeros': self._find_zeros(),
            'sign': self._analyze_sign(),
            'extrema': self._find_extrema(),
            'monotonicity': self._analyze_monotonicity(),
            'parity': self._analyze_parity(),
        }
    
    def _analyze_parametric(self):
        """Анализ параметрической кривой"""
        return {
            'type': 'parametric',
            'parameter_range': f"t ∈ [{self.x_min:.2f}; {self.x_max:.2f}]",
            'x_range': self._parametric_coord_range('x'),
            'y_range': self._parametric_coord_range('y'),
            'curve_length': self._curve_length(),
            'special_points': self._find_special_parametric_points(),
            'self_intersections': self._find_self_intersections(),
            'curvature_extrema': self._find_curvature_extrema(),
            'curve_type': self._identify_curve_type(),
        }

    def to_text(self):
        """Текстовое представление анализа"""
        a = self.analyze()
        
        if a['type'] == 'standard':
            return self._standard_to_text(a)
        elif a['type'] == 'parametric':
            return self._parametric_to_text(a)
    
    def _standard_to_text(self, a):
        """Форматирование для обычной функции"""
        result = f"Анализ функции: f(x) = {self.user_expr}\n\n"
        result += f"• Область определения: {a['domain']}\n"
        result += f"• Множество значений: {a['range']}\n"
        result += f"• Нули функции: {a['zeros']}\n"
        result += f"• Промежутки знакопостоянства:\n   {a['sign']}\n"
        result += f"• Экстремумы:\n   {a['extrema']}\n"
        result += f"• Монотонность:\n   {a['monotonicity']}\n"
        result += f"• Чётность: {a['parity']}"
        return result
    
    def _parametric_to_text(self, a):
        """Форматирование для параметрической кривой"""
        result = f"Анализ параметрической кривой:\n"
        result += f"   x(t) = {self.x_expr}\n"
        result += f"   y(t) = {self.y_expr}\n\n"
        result += f"• Тип кривой: {a['curve_type']}\n"
        result += f"• Диапазон параметра: {a['parameter_range']}\n"
        result += f"• Диапазон x: {a['x_range']}\n"
        result += f"• Диапазон y: {a['y_range']}\n"
        result += f"• Длина кривой: {a['curve_length']}\n"
        result += f"• Особые точки:\n   {a['special_points']}\n"
        result += f"• Самопересечения: {a['self_intersections']}\n"
        result += f"• Экстремумы кривизны:\n   {a['curvature_extrema']}"
        return result

    # ========== МЕТОДЫ ДЛЯ ПАРАМЕТРИЧЕСКИХ КРИВЫХ ==========
    
    def _parametric_coord_range(self, coord='x'):
        """Определение диапазона координаты для параметрической кривой"""
        try:
            func = self.x_func if coord == 'x' else self.y_func
            ts = np.linspace(self.x_min, self.x_max, 1000)
            vals = []
            
            for t in ts:
                try:
                    val = func(t)
                    if np.isfinite(val):
                        vals.append(val)
                except:
                    continue
            
            if not vals:
                return "не определён"
            
            v_min, v_max = min(vals), max(vals)
            return f"[{v_min:.2f}; {v_max:.2f}]"
            
        except Exception as e:
            print(f"⚠️ Ошибка определения диапазона {coord}: {e}")
            return "не определён"
    
    def _curve_length(self):
        """Вычисление длины параметрической кривой"""
        try:
            ts = np.linspace(self.x_min, self.x_max, 2000)
            length = 0
            
            for i in range(len(ts) - 1):
                t1, t2 = ts[i], ts[i + 1]
                
                try:
                    x1, y1 = self.x_func(t1), self.y_func(t1)
                    x2, y2 = self.x_func(t2), self.y_func(t2)
                    
                    if all(np.isfinite([x1, y1, x2, y2])):
                        dx = x2 - x1
                        dy = y2 - y1
                        length += np.sqrt(dx**2 + dy**2)
                except:
                    continue
            
            return f"L ≈ {length:.2f}"
            
        except Exception as e:
            print(f"⚠️ Ошибка вычисления длины: {e}")
            return "не определена"
    
    def _find_special_parametric_points(self):
        """Поиск особых точек параметрической кривой"""
        special = []
        
        try:
            # Точки где dx/dt = 0 (вертикальная касательная)
            if self.dx_dt_sym is not None:
                try:
                    t_vertical = solve(self.dx_dt_sym, self.t_sym)
                    for t in t_vertical:
                        if t.is_real or t.is_real is None:
                            t_val = float(t.evalf())
                            if self.x_min <= t_val <= self.x_max:
                                x_val = self.x_func(t_val)
                                y_val = self.y_func(t_val)
                                special.append(f"Вертикальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
                except:
                    pass
            
            # Точки где dy/dt = 0 (горизонтальная касательная)
            if self.dy_dt_sym is not None:
                try:
                    t_horizontal = solve(self.dy_dt_sym, self.t_sym)
                    for t in t_horizontal:
                        if t.is_real or t.is_real is None:
                            t_val = float(t.evalf())
                            if self.x_min <= t_val <= self.x_max:
                                x_val = self.x_func(t_val)
                                y_val = self.y_func(t_val)
                                special.append(f"Горизонтальная касательная при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
                except:
                    pass
            
            # Точки где dx/dt = dy/dt = 0 (особая точка)
            if self.dx_dt_sym is not None and self.dy_dt_sym is not None:
                try:
                    singular = solve([self.dx_dt_sym, self.dy_dt_sym], self.t_sym)
                    for sol in singular:
                        if isinstance(sol, dict):
                            t_val = float(sol[self.t_sym].evalf())
                        else:
                            t_val = float(sol.evalf())
                        
                        if self.x_min <= t_val <= self.x_max:
                            x_val = self.x_func(t_val)
                            y_val = self.y_func(t_val)
                            special.append(f"Особая точка при t={t_val:.2f}, ({x_val:.2f}, {y_val:.2f})")
                except:
                    pass
            
            if special:
                return "\n   ".join(special[:5])  # Топ-5
            else:
                return "Не найдены"
                
        except Exception as e:
            print(f"⚠️ Ошибка поиска особых точек: {e}")
            return "Не определены"
    
    def _find_self_intersections(self):
        """Поиск самопересечений параметрической кривой"""
        try:
            ts = np.linspace(self.x_min, self.x_max, 500)
            points = {}
            intersections = []
            
            for t in ts:
                try:
                    x = self.x_func(t)
                    y = self.y_func(t)
                    
                    if not (np.isfinite(x) and np.isfinite(y)):
                        continue
                    
                    # Округляем для сравнения
                    key = (round(x, 2), round(y, 2))
                    
                    if key in points:
                        # Проверяем что это не та же точка параметра
                        if abs(t - points[key]) > 0.1:
                            intersections.append((key[0], key[1], points[key], t))
                    else:
                        points[key] = t
                        
                except:
                    continue
            
            if intersections:
                result = []
                for x, y, t1, t2 in intersections[:3]:  # Топ-3
                    result.append(f"({x:.2f}, {y:.2f}) при t₁={t1:.2f}, t₂={t2:.2f}")
                return "\n   ".join(result)
            else:
                return "Не найдены"
                
        except Exception as e:
            print(f"⚠️ Ошибка поиска самопересечений: {e}")
            return "Не определены"
    
    def _find_curvature_extrema(self):
        """Поиск экстремумов кривизны"""
        try:
            # κ = |x'y'' - y'x''| / (x'² + y'²)^(3/2)
            if self.dx_dt_sym is None or self.dy_dt_sym is None:
                return "Не определены"
            
            # Вторые производные
            d2x_dt2 = diff(self.dx_dt_sym, self.t_sym)
            d2y_dt2 = diff(self.dy_dt_sym, self.t_sym)
            
            # Численный поиск экстремумов кривизны
            ts = np.linspace(self.x_min, self.x_max, 500)
            curvatures = []
            
            for t in ts:
                try:
                    dx = float(self.dx_dt_sym.subs(self.t_sym, t))
                    dy = float(self.dy_dt_sym.subs(self.t_sym, t))
                    d2x = float(d2x_dt2.subs(self.t_sym, t))
                    d2y = float(d2y_dt2.subs(self.t_sym, t))
                    
                    numerator = abs(dx * d2y - dy * d2x)
                    denominator = (dx**2 + dy**2)**(3/2)
                    
                    if denominator > 1e-9:
                        k = numerator / denominator
                        curvatures.append((t, k))
                except:
                    continue
            
            if not curvatures:
                return "Не найдены"
            
            # Находим максимум и минимум кривизны
            curvatures.sort(key=lambda x: x[1])
            
            result = []
            if len(curvatures) > 0:
                t_min, k_min = curvatures[0]
                x_min, y_min = self.x_func(t_min), self.y_func(t_min)
                result.append(f"Минимум κ={k_min:.3f} при t={t_min:.2f}, ({x_min:.2f}, {y_min:.2f})")
            
            if len(curvatures) > 1:
                t_max, k_max = curvatures[-1]
                x_max, y_max = self.x_func(t_max), self.y_func(t_max)
                result.append(f"Максимум κ={k_max:.3f} при t={t_max:.2f}, ({x_max:.2f}, {y_max:.2f})")
            
            return "\n   ".join(result) if result else "Не найдены"
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа кривизны: {e}")
            return "Не определены"
    
    def _identify_curve_type(self):
        """Определение типа параметрической кривой"""
        try:
            # Проверяем на окружность: x² + y² = r²
            if self.x_expr_sym is not None and self.y_expr_sym is not None:
                # Подставляем несколько значений t
                test_t = [0, np.pi/4, np.pi/2, np.pi, 3*np.pi/2]
                radii = []
                
                for t_val in test_t:
                    try:
                        x = float(self.x_expr_sym.subs(self.t_sym, t_val))
                        y = float(self.y_expr_sym.subs(self.t_sym, t_val))
                        r = np.sqrt(x**2 + y**2)
                        radii.append(r)
                    except:
                        continue
                
                if radii and max(radii) - min(radii) < 0.1:
                    return f"Окружность (r ≈ {np.mean(radii):.2f})"
            
            # Проверяем на эллипс: (x/a)² + (y/b)² = 1
            # Ищем паттерн cos(t), sin(t)
            x_str = str(self.x_expr_sym).lower()
            y_str = str(self.y_expr_sym).lower()
            
            if 'cos' in x_str and 'sin' in y_str:
                return "Эллипс/Окружность"
            
            # Проверяем на спираль
            if ('cos' in x_str or 'sin' in x_str) and ('t*' in x_str or '*t' in x_str):
                return "Спираль"
            
            # Проверяем на циклоиду
            if ('t' in x_str and 'sin' in x_str) and ('cos' in y_str):
                return "Циклоида"
            
            # Проверяем на лиссажу
            if 'sin' in x_str and 'sin' in y_str:
                return "Фигура Лиссажу"
            
            return "Произвольная кривая"
            
        except Exception as e:
            print(f"⚠️ Ошибка определения типа кривой: {e}")
            return "Не определён"

    # ========== МЕТОДЫ ДЛЯ ОБЫЧНЫХ ФУНКЦИЙ (из предыдущей версии) ==========
    
    def _analyze_domain(self):
        """Анализ области определения"""
        if self.expr_sym is None:
            return self._fallback_domain()
        
        try:
            domain = continuous_domain(self.expr_sym, self.x_sym, S.Reals)
            
            if domain == S.Reals:
                return "D(f) = R"
            elif domain.is_Interval:
                return f"D(f) = {self._format_interval(domain)}"
            elif domain.is_Union:
                parts = [self._format_interval(i) for i in domain.args]
                return f"D(f) = {' U '.join(parts)}"
            elif domain.is_EmptySet:
                return "D(f) = Ø"
            else:
                return "D(f) = R"
                
        except Exception as e:
            print(f"⚠️ Ошибка определения области: {e}")
            return self._fallback_domain()

    def _fallback_domain(self):
        """Эвристическое определение области"""
        expr = self.user_expr.lower()
        
        if 'log(' in expr or 'ln(' in expr:
            if re.search(r'log\(x\s*[-+]', expr):
                return "D(f) зависит от аргумента логарифма"
            return "D(f) = (0; +∞)"
        
        if 'sqrt(' in expr:
            if 'sqrt(x)' in expr.replace(' ', ''):
                return "D(f) = [0; +∞)"
            return "D(f) зависит от подкоренного выражения"
        
        if re.search(r'/\s*x\b', expr) or '1/x' in expr:
            return "D(f) = R \\ {0}"
        
        if 'asin(' in expr or 'acos(' in expr or 'arcsin(' in expr or 'arccos(' in expr:
            return "D(f) = [−1; 1]"
        
        return "D(f) = R"

    def _analyze_range(self):
        """Анализ множества значений"""
        numerical_range = self._numerical_range()
        analytical_range = self._analytical_range()
        
        if analytical_range:
            return analytical_range
        
        return numerical_range

    def _numerical_range(self):
        """Численное определение множества значений"""
        try:
            xs = np.linspace(self.x_min, self.x_max, 2000)
            ys = []
            
            for x in xs:
                try:
                    y = self.func(x)
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

    def _analytical_range(self):
        """Аналитическое определение области значений для простых случаев"""
        expr = self.user_expr.lower()
        
        if re.match(r'^[+-]?\d*\.?\d*\*?x\*\*2\s*[+-]?\s*\d*\.?\d*\*?x?\s*[+-]?\s*\d*\.?\d*$', expr.replace(' ', '')):
            if self.expr_sym:
                try:
                    vertex_x = solve(diff(self.expr_sym, self.x_sym), self.x_sym)
                    if vertex_x:
                        vertex_y = float(self.expr_sym.subs(self.x_sym, vertex_x[0]))
                        if 'x**2' in expr or 'x²' in expr:
                            return f"E(f) = [{vertex_y:.2f}; +∞)"
                        else:
                            return f"E(f) = (−∞; {vertex_y:.2f}]"
                except:
                    pass
        
        if expr in ['sin(x)', 'cos(x)', 'math.sin(x)', 'math.cos(x)']:
            return "E(f) = [−1; 1]"
        
        return None

    def _find_zeros(self):
        """Поиск нулей функции"""
        zeros = []
        
        if self.expr_sym is not None:
            try:
                solutions = solve(self.expr_sym, self.x_sym)
                
                for sol in solutions:
                    if sol.is_real or sol.is_real is None:
                        try:
                            val = float(sol.evalf())
                            if self.x_min <= val <= self.x_max:
                                zeros.append(val)
                        except (TypeError, ValueError):
                            continue
                            
            except Exception as e:
                print(f"⚠️ Аналитический поиск нулей не удался: {e}")
        
        if not zeros:
            zeros = self._numerical_zeros()
        
        zeros = sorted(list(set([round(z, 4) for z in zeros])))
        
        if zeros:
            return ", ".join([f"x = {z}" for z in zeros])
        else:
            return "Нулей нет на отрезке"

    def _numerical_zeros(self):
        """Численный поиск нулей методом перебора с уточнением"""
        zeros = []
        step = (self.x_max - self.x_min) / 1000
        
        for i in range(1000):
            x1 = self.x_min + i * step
            x2 = x1 + step
            
            try:
                y1 = self.func(x1)
                y2 = self.func(x2)
                
                if np.isfinite(y1) and np.isfinite(y2):
                    if y1 * y2 < 0:
                        zero = self._bisect(x1, x2)
                        if zero is not None:
                            zeros.append(zero)
                    elif abs(y1) < 1e-6:
                        zeros.append(x1)
                        
            except:
                continue
        
        return zeros

    def _bisect(self, a, b, tol=1e-6, max_iter=50):
        """Метод деления отрезка пополам для уточнения нуля"""
        try:
            for _ in range(max_iter):
                c = (a + b) / 2
                fc = self.func(c)
                
                if abs(fc) < tol or (b - a) / 2 < tol:
                    return c
                
                fa = self.func(a)
                if fa * fc < 0:
                    b = c
                else:
                    a = c
            
            return (a + b) / 2
        except:
            return None

    def _analyze_sign(self):
        """Анализ знакопостоянства"""
        try:
            zeros_str = self._find_zeros()
            
            zeros_list = []
            if zeros_str != "Нулей нет на отрезке":
                for part in zeros_str.split(','):
                    try:
                        z = float(part.split('=')[1].strip())
                        zeros_list.append(z)
                    except:
                        continue
            
            points = sorted([self.x_min] + zeros_list + [self.x_max])
            
            pos_intervals = []
            neg_intervals = []
            
            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                
                if b - a < 1e-9:
                    continue
                
                mid = (a + b) / 2
                
                try:
                    val = self.func(mid)
                    
                    if not np.isfinite(val):
                        continue
                    
                    if val > 1e-9:
                        pos_intervals.append((a, b))
                    elif val < -1e-9:
                        neg_intervals.append((a, b))
                        
                except:
                    continue
            
            def format_intervals(intervals):
                if not intervals:
                    return "нет"
                parts = []
                for a, b in intervals:
                    left_bracket = '(' if a > self.x_min else '['
                    right_bracket = ')' if b < self.x_max else ']'
                    parts.append(f"{left_bracket}{a:.2f}; {b:.2f}{right_bracket}")
                return ", ".join(parts)
            
            pos_str = format_intervals(pos_intervals)
            neg_str = format_intervals(neg_intervals)
            
            return f"f(x) > 0: {pos_str}\n   f(x) < 0: {neg_str}"
            
        except Exception as e:
            print(f"⚠️ Ошибка анализа знака: {e}")
            return "f(x) > 0: не определено\n   f(x) < 0: не определено"

    def _find_extrema(self):
        """Поиск экстремумов (комбинированный метод)"""
        extrema = []
        
        if self.derivative_sym is not None:
            extrema = self._analytical_extrema()
        
        if not extrema:
            extrema = self._numerical_extrema()
        
        if not extrema:
            return "Не найдены"
        
        lines = []
        for typ, x, y in sorted(extrema, key=lambda e: e[1])[:5]:
            label = "Максимум" if typ == 'max' else "Минимум"
            lines.append(f"{label} при x ≈ {x:.3f}, f(x) ≈ {y:.3f}")
        
        return "\n   ".join(lines)

    def _analytical_extrema(self):
        """Аналитический поиск через производную"""
        extrema = []
        
        try:
            critical_points = solve(self.derivative_sym, self.x_sym)
            
            for cp in critical_points:
                if cp.is_real or cp.is_real is None:
                    try:
                        x_val = float(cp.evalf())
                        
                        if not (self.x_min <= x_val <= self.x_max):
                            continue
                        
                        y_val = self.func(x_val)
                        
                        if not np.isfinite(y_val):
                            continue
                        
                        second_deriv = diff(self.derivative_sym, self.x_sym)
                        second_val = float(second_deriv.subs(self.x_sym, cp).evalf())
                        
                        if second_val > 0:
                            extrema.append(('min', x_val, y_val))
                        elif second_val < 0:
                            extrema.append(('max', x_val, y_val))
                        else:
                            eps = 0.001
                            y_left = self.func(x_val - eps)
                            y_right = self.func(x_val + eps)
                            
                            if y_val > y_left and y_val > y_right:
                                extrema.append(('max', x_val, y_val))
                            elif y_val < y_left and y_val < y_right:
                                extrema.append(('min', x_val, y_val))
                                
                    except (TypeError, ValueError):
                        continue
                        
        except Exception as e:
            print(f"⚠️ Аналитический поиск экстремумов не удался: {e}")
        
        return extrema

    def _numerical_extrema(self):
        """Численный поиск экстремумов"""
        extrema = []
        step = (self.x_max - self.x_min) / 500
        
        for i in range(1, 499):
            x0 = self.x_min + (i - 1) * step
            x1 = self.x_min + i * step
            x2 = self.x_min + (i + 1) * step
            
            try:
                y0 = self.func(x0)
                y1 = self.func(x1)
                y2 = self.func(x2)
                
                if not (np.isfinite(y0) and np.isfinite(y1) and np.isfinite(y2)):
                    continue
                
                if y1 > y0 + 1e-9 and y1 > y2 + 1e-9:
                    extrema.append(('max', x1, y1))
                elif y1 < y0 - 1e-9 and y1 < y2 - 1e-9:
                    extrema.append(('min', x1, y1))
                    
            except:
                continue
        
        filtered = []
        for e in extrema:
            if not any(abs(e[1] - f[1]) < step * 2 for f in filtered):
                filtered.append(e)
        
        return filtered

    def _analyze_monotonicity(self):
        """Анализ монотонности функции"""
        try:
            if self.derivative_sym is not None:
                return self._analytical_monotonicity()
            else:
                return self._numerical_monotonicity()
        except Exception as e:
            print(f"⚠️ Ошибка анализа монотонности: {e}")
            return "не определена"

    def _analytical_monotonicity(self):
        """Аналитический анализ монотонности через производную"""
        try:
            critical_points = solve(self.derivative_sym, self.x_sym)
            
            crit_vals = []
            for cp in critical_points:
                if cp.is_real or cp.is_real is None:
                    try:
                        val = float(cp.evalf())
                        if self.x_min <= val <= self.x_max:
                            crit_vals.append(val)
                    except:
                        continue
            
            points = sorted([self.x_min] + crit_vals + [self.x_max])
            
            increasing = []
            decreasing = []
            
            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                mid = (a + b) / 2
                
                try:
                    deriv_val = float(self.derivative_sym.subs(self.x_sym, mid).evalf())
                    
                    if deriv_val > 1e-6:
                        increasing.append((a, b))
                    elif deriv_val < -1e-6:
                        decreasing.append((a, b))
                except:
                    continue
            
            return self._format_monotonicity(increasing, decreasing)
            
        except Exception as e:
            print(f"⚠️ Аналитическая монотонность не удалась: {e}")
            return self._numerical_monotonicity()

    def _numerical_monotonicity(self):
        """Численный анализ монотонности"""
        increasing = []
        decreasing = []
        
        step = (self.x_max - self.x_min) / 100
        current_interval = None
        current_type = None
        
        for i in range(99):
            x1 = self.x_min + i * step
            x2 = x1 + step
            
            try:
                y1 = self.func(x1)
                y2 = self.func(x2)
                
                if not (np.isfinite(y1) and np.isfinite(y2)):
                    if current_interval:
                        if current_type == 'inc':
                            increasing.append(current_interval)
                        else:
                            decreasing.append(current_interval)
                        current_interval = None
                    continue
                
                if y2 > y1 + 1e-6:
                    interval_type = 'inc'
                elif y2 < y1 - 1e-6:
                    interval_type = 'dec'
                else:
                    continue
                
                if current_interval is None:
                    current_interval = (x1, x2)
                    current_type = interval_type
                elif current_type == interval_type:
                    current_interval = (current_interval[0], x2)
                else:
                    if current_type == 'inc':
                        increasing.append(current_interval)
                    else:
                        decreasing.append(current_interval)
                    current_interval = (x1, x2)
                    current_type = interval_type
                    
            except:
                continue
        
        if current_interval:
            if current_type == 'inc':
                increasing.append(current_interval)
            else:
                decreasing.append(current_interval)
        
        return self._format_monotonicity(increasing, decreasing)

    def _format_monotonicity(self, increasing, decreasing):
        """Форматирование результатов монотонности"""
        def format_intervals(intervals):
            if not intervals:
                return "нет"
            parts = []
            for a, b in intervals:
                parts.append(f"[{a:.2f}; {b:.2f}]")
            return ", ".join(parts)
        
        inc_str = format_intervals(increasing)
        dec_str = format_intervals(decreasing)
        
        return f"Возрастает: {inc_str}\n   Убывает: {dec_str}"

    def _analyze_parity(self):
        """Анализ чётности функции"""
        if abs(self.x_min + self.x_max) > 1e-6:
            return "общего вида (область несимметрична)"
        
        if self.expr_sym is not None:
            try:
                expr_minus_x = self.expr_sym.subs(self.x_sym, -self.x_sym)
                
                if simplify(expr_minus_x - self.expr_sym) == 0:
                    return "чётная"
                
                if simplify(expr_minus_x + self.expr_sym) == 0:
                    return "нечётная"
                
            except Exception as e:
                print(f"⚠️ Аналитическая проверка чётности не удалась: {e}")
        
        test_points = np.linspace(0.1, min(3.0, self.x_max), 10)
        even = True
        odd = True
        
        for x in test_points:
            if x > self.x_max or -x < self.x_min:
                break
            
            try:
                fx = self.func(x)
                fmx = self.func(-x)
                
                if not (np.isfinite(fx) and np.isfinite(fmx)):
                    even = odd = False
                    break
                
                if abs(fx - fmx) > 1e-4:
                    even = False
                
                if abs(fx + fmx) > 1e-4:
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

    def _format_interval(self, iv):
        """Форматирование интервала для вывода"""
        if iv == S.Reals:
            return "R"
        
        left = str(iv.start).replace('oo', '∞').replace('-∞', '−∞')
        right = str(iv.end).replace('oo', '∞')
        
        lbracket = '[' if not iv.left_open else '('
        rbracket = ']' if not iv.right_open else ')'
        
        return f"{lbracket}{left}; {right}{rbracket}"