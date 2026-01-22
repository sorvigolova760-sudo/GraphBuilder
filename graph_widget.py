# graph_widget.py
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.core.text import Label as CoreLabel
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
        self.functions = []  # список функций
        self.intersection_points = []  # точки пересечения
        self.graph_padding = dp(20)
        self.bind(size=self.on_size, pos=self.on_size)

    def on_size(self, *args):
        self.draw()

    def set_functions(self, funcs):
        self.functions = funcs if funcs else []
        self.intersection_points = []

    def set_ranges(self, x_min, x_max, y_min, y_max):
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        if self.function:
            self.draw()

    def draw(self):
        self.canvas.clear()
        self.points = []
    
        # Используем self.functions вместо self.function
        if not self.functions:
            return

        self.graph_area = (
            self.x + self.graph_padding,
            self.y + self.graph_padding,
            self.width - 2 * self.graph_padding,
            self.height - 2 * self.graph_padding
        )
        graph_x, graph_y, graph_width, graph_height = self.graph_area
        side = min(graph_width, graph_height)
        square_x = graph_x + (graph_width - side) / 2
        square_y = graph_y + (graph_height - side) / 2
        square_size = side

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=(square_x, square_y), size=(square_size, square_size))
            Color(0.6, 0.6, 0.6, 0.8)
            self._draw_grid(square_x, square_y, square_size, square_size)
            Color(0.3, 0.3, 0.3, 1)
            self._draw_axes(square_x, square_y, square_size, square_size)
        
            # Рисуем все функции
            self._draw_function(square_x, square_y, square_size, square_size)
        
            Color(0.8, 0.8, 0.8, 0.3)
            Line(rectangle=(square_x, square_y, square_size, square_size), width=1)

    def _draw_grid(self, area_x, area_y, area_size, area_height):
        x_pixels_per_unit = area_size / (self.x_max - self.x_min)
        y_pixels_per_unit = area_size / (self.y_max - self.y_min)
        pixels_per_unit = min(x_pixels_per_unit, y_pixels_per_unit)
        desired_lines = 10
        unit_step_x = (self.x_max - self.x_min) / desired_lines
        unit_step_y = (self.y_max - self.y_min) / desired_lines
        unit_step = max(unit_step_x, unit_step_y)
        unit_step = self._nice_number(unit_step)

        x_start = math.ceil(self.x_min / unit_step) * unit_step
        x_end = math.floor(self.x_max / unit_step) * unit_step
        x = x_start
        while x <= x_end + unit_step/100:
            screen_x = self._x_to_screen(x, area_x, area_size)
            if area_x <= screen_x <= area_x + area_size:
                Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=0.5)
            x += unit_step

        y_start = math.ceil(self.y_min / unit_step) * unit_step
        y_end = math.floor(self.y_max / unit_step) * unit_step
        y = y_start
        while y <= y_end + unit_step/100:
            screen_y = self._y_to_screen(y, area_y, area_size)
            if area_y <= screen_y <= area_y + area_size:
                Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=0.5)
            y += unit_step

    def _nice_number(self, value):
        if value <= 0:
            return 1.0
        exponent = math.floor(math.log10(value))
        fraction = value / (10 ** exponent)
        nice_fractions = [1, 2, 5, 10]
        nice_fraction = min(nice_fractions, key=lambda x: abs(x - fraction))
        return nice_fraction * (10 ** exponent)

    def _draw_axes(self, area_x, area_y, area_size, area_height):
        """Рисует оси координат с подписями"""
        # Ось X (где y=0)
        screen_y = self._y_to_screen(0, area_y, area_size)
        if area_y <= screen_y <= area_y + area_size:
            Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=1.5)
            # Стрелка
            arrow_size = 8
            Line(points=[
                area_x + area_size - arrow_size, screen_y - arrow_size/2,
                area_x + area_size, screen_y,
                area_x + area_size - arrow_size, screen_y + arrow_size/2
            ], width=1.5)

        # Ось Y (где x=0)
        screen_x = self._x_to_screen(0, area_x, area_size)
        if area_x <= screen_x <= area_x + area_size:
            Line(points=[screen_x, area_y, screen_x, area_y + area_size], width=1.5)
            # Стрелка
            arrow_size = 8
            Line(points=[
                screen_x - arrow_size/2, area_y + area_size - arrow_size,
                screen_x, area_y + area_size,
                screen_x + arrow_size/2, area_y + area_size - arrow_size
            ], width=1.5)

        # === Подписи на осях ===
        self._draw_axis_labels(area_x, area_y, area_size, area_height)

    def _draw_axis_labels(self, area_x, area_y, area_size, area_height):
        """Рисует текстовые подписи рядом с осями координат (а не по краям области)"""
        font_size = dp(12)
        label_color = (0.2, 0.2, 0.2, 1)

        # === Подписи на оси X (рядом с линией y=0) ===
        x_unit_step = self._nice_number((self.x_max - self.x_min) / 8)
        x_start = math.ceil(self.x_min / x_unit_step) * x_unit_step
        x_end = math.floor(self.x_max / x_unit_step) * x_unit_step
        x = x_start
        while x <= x_end + x_unit_step / 100:
            if abs(x) > 0.01:  # Пропускаем 0
                screen_x = self._x_to_screen(x, area_x, area_size)
                screen_y_axis_x = self._y_to_screen(0, area_y, area_size)  # Позиция оси X (y=0)
            
                if area_x <= screen_x <= area_x + area_size and area_y <= screen_y_axis_x <= area_y + area_size:
                    label = CoreLabel(
                        text=str(round(x, 2)),
                        font_size=font_size,
                        color=label_color
                    )
                    label.refresh()
                    texture = label.texture
                    # Позиционируем ПОД осью X
                    label_x = screen_x - texture.width / 2
                    label_y = screen_y_axis_x - texture.height - dp(3)
                    # Убедимся, что не выходит за пределы карточки
                    if label_y >= area_y - texture.height - dp(10):
                        Color(*label_color)
                        Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
            x += x_unit_step

        # === Подписи на оси Y (рядом с линией x=0) ===
        y_unit_step = self._nice_number((self.y_max - self.y_min) / 8)
        y_start = math.ceil(self.y_min / y_unit_step) * y_unit_step
        y_end = math.floor(self.y_max / y_unit_step) * y_unit_step
        y = y_start
        while y <= y_end + y_unit_step / 100:
            if abs(y) > 0.01:  # Пропускаем 0
                screen_y = self._y_to_screen(y, area_y, area_size)
                screen_x_axis_y = self._x_to_screen(0, area_x, area_size)  # Позиция оси Y (x=0)

                if area_y <= screen_y <= area_y + area_size and area_x <= screen_x_axis_y <= area_x + area_size:
                    label = CoreLabel(
                        text=str(round(y, 2)),
                        font_size=font_size,
                        color=label_color
                    )
                    label.refresh()
                    texture = label.texture
                    # Позиционируем СЛЕВА от оси Y
                    label_x = screen_x_axis_y - texture.width - dp(5)
                    label_y = screen_y - texture.height / 2
                    if label_x >= area_x - texture.width - dp(10):
                        Color(*label_color)
                        Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
            y += y_unit_step


    # Обнови _draw_function:
    def _draw_function(self, area_x, area_y, area_size, area_height):
        if not self.functions:
            return

        colors = [(0, 0, 1), (1, 0, 0)]  # синий, красный

        for idx, func in enumerate(self.functions):
            points = []
            num_points = max(1000, int(area_size * 3))
            for i in range(num_points + 1):
                x = self.x_min + (i / num_points) * (self.x_max - self.x_min)
                try:
                    y = func(x)
                    if math.isnan(y) or math.isinf(y):
                        if len(points) > 2:
                            Color(*colors[idx])
                            Line(points=points, width=2.5, cap='round', joint='round')
                        points = []
                        continue

                    if y < self.y_min or y > self.y_max:
                        if len(points) > 2:
                            Color(*colors[idx])
                            Line(points=points, width=2.5, cap='round', joint='round')
                        points = []
                        continue

                    screen_x = self._x_to_screen(x, area_x, area_size)
                    screen_y = self._y_to_screen(y, area_y, area_size)

                    if area_x <= screen_x <= area_x + area_size:
                        points.append(screen_x)
                        points.append(screen_y)
                    else:
                        if len(points) > 2:
                            Color(*colors[idx])
                            Line(points=points, width=2.5, cap='round', joint='round')
                        points = []

                except Exception:
                    if len(points) > 2:
                        Color(*colors[idx])
                        Line(points=points, width=2.5, cap='round', joint='round')
                    points = []
                    continue

            if len(points) >= 2:
                Color(*colors[idx])
                Line(points=points, width=2.5, cap='round', joint='round')

        # Рисуем точки пересечения
        if self.intersection_points:
            print(f"РИСУЮ {len(self.intersection_points)} точек")
            Color(0, 0, 0)  # чёрный
            for x, y in self.intersection_points:
                screen_x = self._x_to_screen(x, area_x, area_size)
                screen_y = self._y_to_screen(y, area_y, area_size)  # ← исправлено
                if area_x <= screen_x <= area_x + area_size and area_y <= screen_y <= area_y + area_size:
                    Ellipse(pos=(screen_x - 4, screen_y - 4), size=(8, 8))

    def _x_to_screen(self, x, area_x, area_size):
        return area_x + ((x - self.x_min) / (self.x_max - self.x_min)) * area_size

    def _y_to_screen(self, y, area_y, area_size):
        normalized_y = (y - self.y_min) / (self.y_max - self.y_min)
        return area_y + normalized_y * area_size