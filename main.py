#!/usr/bin/env python3
"""
График функций - правильная структура интерфейса
"""

import os

# Настройки для Linux
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_WINDOW'] = 'sdl2'

print("=" * 60)
print("График функций")
print("=" * 60)

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard

from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp
import math

class GraphWidget(Widget):
    """Виджет для рисования графика"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.function = None
        self.x_min = -5
        self.x_max = 5
        self.y_min = -5
        self.y_max = 5
        self.points = []
        # Определяем область отрисовки (отступы от краев)
        self.graph_padding = dp(20)  # Отступ от краев
        self.graph_area = None  # Будет установлено в draw()
    
    def on_size(self, *args):
        self.draw()
        
    def set_function(self, func):
        """Устанавливает функцию для рисования"""
        self.function = func
        self.draw()
        
    def set_ranges(self, x_min, x_max, y_min, y_max):
        """Устанавливает диапазоны"""
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        if self.function:
            self.draw()
    
    def draw(self):
        """Рисует график"""
        self.canvas.clear()
        self.points = []
        
        if not self.function:
            return
            
        # Определяем область отрисовки графика (с отступами)
        self.graph_area = (
            self.x + self.graph_padding,
            self.y + self.graph_padding,
            self.width - 2 * self.graph_padding,
            self.height - 2 * self.graph_padding
        )
        
        graph_x, graph_y, graph_width, graph_height = self.graph_area
        
        # Делаем область квадратной, сохраняя пропорции
        # Используем минимальную из сторон для квадратной области
        side = min(graph_width, graph_height)
        
        # Центрируем квадратную область
        square_x = graph_x + (graph_width - side) / 2
        square_y = graph_y + (graph_height - side) / 2
        square_size = side
        
        with self.canvas:
            # Белый фон ТОЛЬКО в квадратной области графика
            Color(1, 1, 1, 1)
            Rectangle(pos=(square_x, square_y), size=(square_size, square_size))
            # Сетка (светло-серая)
            Color(0.9, 0.9, 0.9, 0.5)
            self._draw_grid(square_x, square_y, square_size, square_size)
            # Оси (темно-серые)
            Color(0.3, 0.3, 0.3, 1)
            self._draw_axes(square_x, square_y, square_size, square_size)
            # График функции (фиолетовый)
            Color(0.4, 0.35, 0.85, 1)
            self._draw_function(square_x, square_y, square_size, square_size)
            # Рамка вокруг квадратной области (для отладки, можно убрать)
            Color(0.8, 0.8, 0.8, 0.3)
            Line(rectangle=(square_x, square_y, square_size, square_size), width=1)
    
    def _draw_grid(self, area_x, area_y, area_size, area_height):
        """Рисует координатную сетку"""
        # Для квадратной сетки используем одинаковые шаги по X и Y
        
        # Вычисляем физическое соотношение пикселей
        x_pixels_per_unit = area_size / (self.x_max - self.x_min)
        y_pixels_per_unit = area_size / (self.y_max - self.y_min)
        
        # Используем меньший шаг для более частой сетки
        pixels_per_unit = min(x_pixels_per_unit, y_pixels_per_unit)
        
        # Определяем оптимальный шаг в единицах координат
        # Желаем примерно 10-20 линий на графике
        desired_lines = 10
        unit_step_x = (self.x_max - self.x_min) / desired_lines
        unit_step_y = (self.y_max - self.y_min) / desired_lines
        
        # Используем больший шаг для меньшего количества линий
        unit_step = max(unit_step_x, unit_step_y)
        
        # Округляем до красивых значений (1, 2, 5, 10, ...)
        unit_step = self._nice_number(unit_step)
        
        # Вертикальные линии (параллельны оси Y)
        x_start = math.ceil(self.x_min / unit_step) * unit_step
        x_end = math.floor(self.x_max / unit_step) * unit_step
        
        x = x_start
        while x <= x_end + unit_step/100:  # Добавляем epsilon для погрешности
            screen_x = self._x_to_screen(x, area_x, area_size)
            if area_x <= screen_x <= area_x + area_size:
                Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=0.5)
            x += unit_step
        
        # Горизонтальные линии (параллельны оси X)
        y_start = math.ceil(self.y_min / unit_step) * unit_step
        y_end = math.floor(self.y_max / unit_step) * unit_step
        
        y = y_start
        while y <= y_end + unit_step/100:  # Добавляем epsilon для погрешности
            screen_y = self._y_to_screen(y, area_y, area_size)
            if area_y <= screen_y <= area_y + area_size:
                Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=0.5)
            y += unit_step
    
    def _nice_number(self, value):
        """Округляет число до красивых значений (1, 2, 5, 10, ...)"""
        if value <= 0:
            return 1.0
        
        exponent = math.floor(math.log10(value))
        fraction = value / (10 ** exponent)
        
        nice_fractions = [1, 2, 5, 10]
        nice_fraction = min(nice_fractions, key=lambda x: abs(x - fraction))
        
        return nice_fraction * (10 ** exponent)
    
    def _draw_axes(self, area_x, area_y, area_size, area_height):
        """Рисует оси координат"""
        # Ось X (где y=0)
        screen_y = self._y_to_screen(0, area_y, area_size)
        if area_y <= screen_y <= area_y + area_size:
            Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=1.5)
            
            # Стрелка оси X
            arrow_size = 8
            Line(points=[
                area_x + area_size - arrow_size, screen_y - arrow_size/2,
                area_x + area_size, screen_y,
                area_x + area_size - arrow_size, screen_y + arrow_size/2
            ], width=1.5)
            
            # Подписи оси X (каждые 2 единицы)
            unit_step = self._nice_number((self.x_max - self.x_min) / 10)
            x_start = math.ceil(self.x_min / unit_step) * unit_step
            x_end = math.floor(self.x_max / unit_step) * unit_step
            
            x = x_start
            while x <= x_end + unit_step/100:
                if abs(x) > 0.01:  # Не подписываем 0 (он будет на оси Y)
                    screen_x = self._x_to_screen(x, area_x, area_size)
                    # Можно добавить текстовые подписи здесь при необходимости
                x += unit_step
        
        # Ось Y (где x=0)
        screen_x = self._x_to_screen(0, area_x, area_size)
        if area_x <= screen_x <= area_x + area_size:
            Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=1.5)
            
            # Стрелка оси Y
            arrow_size = 8
            Line(points=[
                screen_x - arrow_size/2, area_y + area_size - arrow_size,
                screen_x, area_y + area_size,
                screen_x + arrow_size/2, area_y + area_size - arrow_size
            ], width=1.5)
            
            # Подписи оси Y (каждые 2 единицы)
            unit_step = self._nice_number((self.y_max - self.y_min) / 10)
            y_start = math.ceil(self.y_min / unit_step) * unit_step
            y_end = math.floor(self.y_max / unit_step) * unit_step
            
            y = y_start
            while y <= y_end + unit_step/100:
                if abs(y) > 0.01:  # Не подписываем 0 (он будет на оси X)
                    screen_y = self._y_to_screen(y, area_y, area_size)
                    # Можно добавить текстовые подписи здесь при необходимости
                y += unit_step
    
    def _draw_function(self, area_x, area_y, area_size, area_height):
        """Рисует график функции"""
        if not self.function:
            return
    
        points = []
        num_points = int(area_size * 2)  # Увеличиваем количество точек для гладкости
    
        for i in range(num_points + 1):
            x = self.x_min + (i / num_points) * (self.x_max - self.x_min)
            try:
                y = self.function(x)
                # Обрабатываем inf и -inf
                if math.isinf(y):
                    # Разрыв графика
                    if len(points) > 2:
                        Line(points=points, width=2.5)
                    points = []
                    self.points.append(None)
                    continue
                
                if not math.isnan(y):
                    screen_x = self._x_to_screen(x, area_x, area_size)
                    screen_y = self._y_to_screen(y, area_y, area_size)
                
                    # Проверяем, находится ли точка в пределах области графика
                    # Добавляем небольшой запас для плавного рисования
                    margin = 0  # Увеличиваем запас
                    if (area_y - margin <= screen_y <= area_y + area_size + margin and
                        area_x - margin <= screen_x <= area_x + area_size + margin):
                        points.append(screen_x)
                        points.append(screen_y)
                        self.points.append((x, y))
                    else:
                        # Разрыв графика
                        if len(points) > 2:
                            Line(points=points, width=2.5)
                        points = []
                        self.points.append(None)
            except Exception as e:
                # Для отладки
                if len(points) > 2:
                    Line(points=points, width=2.5)
                points = []
                self.points.append(None)
                continue
    
        # Рисуем оставшиеся точки
        if len(points) > 2:
            Line(points=points, width=2.5)
        elif len(points) == 2:
            # Если только одна точка (2 координаты)
            Line(points=points, width=2.5)

    def _x_to_screen(self, x, area_x, area_size):
        """Преобразует координату X в экранные координаты"""
        return area_x + ((x - self.x_min) / (self.x_max - self.x_min)) * area_size
    
    def _y_to_screen(self, y, area_y, area_size):
        normalized_y = (y - self.y_min) / (self.y_max - self.y_min)
        return area_y + normalized_y * area_size
    
class FunctionParser:
    """Окончательный исправленный парсер"""
    
    @staticmethod
    def parse(expr):
        import math
        import re
        
        print(f"\n🔧 ПАРСЕР: Обработка: '{expr}'")
        
        # 1. Сохраняем исходное выражение для отладки
        original = expr
        
        # 2. Приводим к нижнему регистру (для простоты)
        expr = expr.lower().strip()
        
        # 3. Заменяем степени
        expr = expr.replace('^', '**')
        expr = expr.replace('²', '**2')
        expr = expr.replace('³', '**3')
        # Не заменяем 'pi' и 'e' в строке — они будут в контексте
        
        # 4. ЗАМЕНА ФУНКЦИЙ с использованием \b (границы слова)
        # Порядок не критичен благодаря \b, но логично сначала обрабатывать asin, потом sin
        # ЗАМЕНА ФУНКЦИЙ с защитой от повторной замены внутри math.
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
        
        # 5. Теперь безопасное неявное умножение
        
        # а) 2x -> 2*x (цифра перед буквой)
        expr = re.sub(r'(\d)(?![.\d])([a-zA-Z])', r'\1*\2', expr)
        
        # б) x( -> x*(, но не если перед ( уже есть *
        # Используем негативный просмотр назад, чтобы не трогать math.sin(
        expr = re.sub(r'(?<!\*)\b([a-zA-Z\)])\(', r'\1*(', expr)
        
        # в) )x -> )*x
        expr = re.sub(r'(\))([a-zA-Z\d])', r'\1*\2', expr)
        
        # г) x2 -> x*2
        expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)
        
        print(f"🔧 После умножения: '{expr}'")
        
        # 6. Финальная очистка: убираем артефакты вроде math.sin*( 
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
        
        # 8. Быстрый тест (исправлен вывод)
        print("🔧 Тест парсера:")
        test_values = [0, 1.57, 3.14]
        for val in test_values:
            y = func(val)
            print(f"  f({val:.2f}) = {y}")
        
        return func


# Тестируем прямо в коде
if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТ ПАРСЕРА")
    print("=" * 60)
    
    parser = FunctionParser
    
    test_cases = [
        "sin(x)",
        "cos(x)",
        "tan(x)",
        "x**2",
        "2*x+1",
        "sqrt(x)",
        "log(x)",
    ]
    
    for expr in test_cases:
        print(f"\n📊 Тест: {expr}")
        try:
            func = parser.parse(expr)
            
            # Тестируем на нескольких значениях
            if "sin" in expr:
                test_points = [0, 1.57, 3.14]  # 0, π/2, π
            elif "cos" in expr:
                test_points = [0, 1.57, 3.14]
            elif "tan" in expr:
                test_points = [0, 0.78, 1.57]  # 0, π/4, π/2
            elif "sqrt" in expr:
                test_points = [0, 1, 4]
            elif "log" in expr:
                test_points = [1, 2.72, 10]  # 1, e, 10
            else:
                test_points = [-2, -1, 0, 1, 2]
            
            for x in test_points:
                y = func(x)
                status = "✓" if not (isinstance(y, float) and math.isnan(y)) else "✗ (NaN)"
                print(f"  f({x:.2f}) = {y:.4f} {status}")
                
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
            
class GraphFunctionApp(MDApp):
    """Главное приложение"""
    
    def build(self):
        # Настройка темы
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Light"
        
        # Главный layout - вертикальный
        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(10)
        )
        
        # === ВЕРХНЯЯ ПАНЕЛЬ: Заголовок и ввод ===
        top_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(150),
            spacing=dp(10)
        )
        
        # Заголовок
        title = MDLabel(
            text="Построитель графиков функций",
            halign="center",
            font_style="H5",
            theme_text_color="Primary",
            size_hint=(1, None),
            height=dp(40)
        )
        top_panel.add_widget(title)
        
        # Карточка для ввода функции
        input_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(100),
            elevation=2
        )
        
        input_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10))
        
        # Поле ввода функции
        self.func_input = MDTextField(
            text="x**2",
            hint_text="Введите функцию",
            mode="rectangle",
            size_hint=(0.7, None),
            height=dp(50),
            font_size='16sp'
        )
        
        # Кнопка построения
        plot_btn = MDRaisedButton(
            text="Построить",
            size_hint=(0.3, None),
            height=dp(50),
            on_press=self.plot_function
        )
        
        input_layout.add_widget(self.func_input)
        input_layout.add_widget(plot_btn)
        input_card.add_widget(input_layout)
        
        top_panel.add_widget(input_card)
        main_layout.add_widget(top_panel)
        
        # === СРЕДНЯЯ ПАНЕЛЬ: График ===
        # Карточка с четкими границами для области графика
        graph_card = MDCard(
            padding=dp(10),
            size_hint=(1, 0.6),  # 60% высоты
            elevation=3,
            radius=[15, 15, 15, 15],  # Закругленные углы
            md_bg_color=(0.95, 0.95, 0.95, 1)  # Светло-серый фон карточки
        )
        
        self.graph = GraphWidget()
        graph_card.add_widget(self.graph)
        
        main_layout.add_widget(graph_card)

        # === НИЖНЯЯ ПАНЕЛЬ: Управление и примеры ===
        bottom_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(250),
            spacing=dp(10)
        )
        
        # Панель управления диапазонами
        control_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(120),
            elevation=2
        )
        
        control_title = MDLabel(
            text="Диапазоны отображения:",
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        control_card.add_widget(control_title)
        
        # Сетка для полей ввода диапазонов
        range_grid = MDGridLayout(cols=4, spacing=dp(10), size_hint=(1, None), height=dp(50))
        
        self.x_min_input = MDTextField(
            text="-5", 
            hint_text="X min",
            mode="rectangle",
            input_filter="float"
        )
        self.x_max_input = MDTextField(
            text="5", 
            hint_text="X max",
            mode="rectangle",
            input_filter="float"
        )
        self.y_min_input = MDTextField(
            text="-5", 
            hint_text="Y min",
            mode="rectangle",
            input_filter="float"
        )
        self.y_max_input = MDTextField(
            text="5", 
            hint_text="Y max",
            mode="rectangle",
            input_filter="float"
        )
        
        range_grid.add_widget(self.x_min_input)
        range_grid.add_widget(self.x_max_input)
        range_grid.add_widget(self.y_min_input)
        range_grid.add_widget(self.y_max_input)
        
        control_card.add_widget(range_grid)
        bottom_panel.add_widget(control_card)
        
        # Панель примеров функций
        examples_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(120),
            elevation=2
        )
        
        examples_title = MDLabel(
            text="Примеры функций:",
            font_style="Subtitle1",
            size_hint=(1, None),
            height=dp(30)
        )
        examples_card.add_widget(examples_title)
        
        # Сетка кнопок примеров
        examples_grid = MDGridLayout(cols=4, spacing=dp(5), size_hint=(1, 1))
        
        examples = [
            ("x²", "x**2", (-5, 5, -5, 5)),
            ("sin(x)", "sin(x)", (-10, 10, -2, 2)),
            ("cos(x)", "cos(x)", (-10, 10, -2, 2)),
            ("tan(x)", "tan(x)", (-3, 3, -5, 5)),
            ("2x+1", "2*x+1", (-5, 5, -5, 5)),
            ("√x", "sqrt(x)", (0, 10, 0, 4)),
            ("1/x", "1/x", (-5, 5, -5, 5)),
            ("exp(x)", "exp(x)", (-2, 4, -1, 20))
        ]
        
        for name, expr, ranges in examples:
            btn = MDFlatButton(
                text=name,
                size_hint=(1, None),
                height=dp(40),
                theme_text_color="Primary",
                on_press=lambda instance, e=expr, r=ranges: self.set_example(e, r)
            )
            examples_grid.add_widget(btn)
        
        examples_card.add_widget(examples_grid)
        bottom_panel.add_widget(examples_card)
        
        main_layout.add_widget(bottom_panel)
        
        # Автоматическое построение графика при запуске
        Clock.schedule_once(lambda dt: self.plot_function(), 0.5)
        
        return main_layout
    
    def plot_function(self, *args):
        """Строит график функции"""
        # Скрываем карточку анализа при новом построении
        try:
            # Получаем функцию
            expr = self.func_input.text.strip()
            if not expr:
                return
        
            # Парсим функцию
            parser = FunctionParser()
            func = parser.parse(expr)
        
            # Получаем диапазоны
            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)
            y_min = float(self.y_min_input.text)
            y_max = float(self.y_max_input.text)
        
            # Проверяем корректность диапазонов
            if x_min >= x_max or y_min >= y_max:
                print("Ошибка: некорректные диапазоны")
                return
        
            print(f"\n{'='*60}")
            print(f"ФУНКЦИЯ: {expr}")
            print(f"Диапазон: X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}]")
            print(f"{'='*60}")
        
            # ПРОСТОЙ ТЕСТ: вычисляем sin(0), должен быть 0
            if 'sin' in expr.lower():
                print(f"ПРОВЕРКА sin: sin(0) должен быть 0")
                test_result = func(0)
                print(f"  sin(0) = {test_result}")
                if math.isnan(test_result):
                    print(f"  ⚠️ ВНИМАНИЕ: sin(0) вернул NaN! Проблема в парсере!")
        
            # Тестируем несколько точек
            test_points = [
                x_min,
                x_min + (x_max - x_min) * 0.25,
                x_min + (x_max - x_min) * 0.5,
                x_min + (x_max - x_min) * 0.75,
                x_max
            ]
        
            print("Тестовые точки:")
            for x in test_points:
                y = func(x)
                if math.isnan(y):
                    print(f"  f({x:.2f}) = NaN (не число)")
                elif math.isinf(y):
                    print(f"  f({x:.2f}) = {'+∞' if y > 0 else '-∞'} (бесконечность)")
                else:
                    print(f"  f({x:.2f}) = {y:.4f}")
        
            # Устанавливаем функцию и диапазоны
            self.graph.set_function(func)
            self.graph.set_ranges(x_min, x_max, y_min, y_max)
        
            print(f"✓ График построен: {expr}")
            print(f"{'='*60}\n")
        
        except ValueError as e:
            print(f"✗ Ошибка ввода: {e}")
        except Exception as e:
            print(f"✗ Ошибка построения графика: {e}")
            import traceback
            traceback.print_exc()

    def set_example(self, expr, ranges):
        """Устанавливает пример функции"""
        self.func_input.text = expr
        self.x_min_input.text = str(ranges[0])
        self.x_max_input.text = str(ranges[1])
        self.y_min_input.text = str(ranges[2])
        self.y_max_input.text = str(ranges[3])
        self.plot_function()
    



if __name__ == '__main__':
    # Тест функции
    print("Тестирование парсера...")
    parser = FunctionParser()
    
    test_functions = [
        ("x**2", "Парабола"),
        ("sin(x)", "Синус"),
        ("cos(x)", "Косинус"),
        ("1/x", "Гипербола")
    ]
    
    for expr, name in test_functions:
        try:
            func = parser.parse(expr)
            print(f"\n{name} ({expr}):")
            for x in [-2, -1, 0, 1, 2]:
                try:
                    y = func(x)
                    print(f"  f({x}) = {y}")
                except:
                    print(f"  f({x}) = ошибка")
        except Exception as e:
            print(f"\nОшибка парсинга {expr}: {e}")
    
    # Запуск приложения
    GraphFunctionApp().run()