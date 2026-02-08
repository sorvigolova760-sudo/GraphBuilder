"""
Виджет для рисования графика
"""
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
        # Для параметрических функций
        self.t_min = 0
        self.t_max = 6.28
        self.points = []
        self.functions = []
        self.intersection_points = []
        self.is_parametric = False
        self.x_func = None
        self.y_func = None
        self.graph_padding = dp(20)
        self.bind(size=self.on_size, pos=self.on_size)

    def set_parametric(self, x_func, y_func, t_min=0, t_max=6.28):
        """
        Устанавливает параметрические функции с диапазоном t
        """
        print(f"🔧 GraphWidget.set_parametric вызван")
        print(f"   t ∈ [{t_min}, {t_max}]")
        self.is_parametric = True
        self.x_func = x_func
        self.y_func = y_func
        self.t_min = t_min
        self.t_max = t_max
        self.functions = []
        self.intersection_points = []

    def on_size(self, *args):
        self.draw()

    def set_functions(self, funcs):
        """
        Устанавливает обычные функции
        """
        self.is_parametric = False
        self.x_func = None
        self.y_func = None
        self.functions = funcs if funcs else []
        self.intersection_points = []

    def set_ranges(self, x_min, x_max, y_min, y_max):
        """
        Устанавливает видимую область графика
        """
        self.x_min = float(x_min)
        self.x_max = float(x_max)
        self.y_min = float(y_min)
        self.y_max = float(y_max)
        if self.function or self.functions or self.is_parametric:
            self.draw()

    def draw(self):
        self.canvas.clear()
        self.points = []

        if not self.functions and not (self.is_parametric and self.x_func and self.y_func):
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

            # Рисуем в зависимости от режима
            if self.is_parametric:
                self._draw_parametric(square_x, square_y, square_size, square_size)
            else:
                self._draw_function(square_x, square_y, square_size, square_size)

            Color(0.8, 0.8, 0.8, 0.3)
            Line(rectangle=(square_x, square_y, square_size, square_size), width=1)

    def _draw_parametric(self, area_x, area_y, area_size, area_height):
        """
        Рисует параметрическую кривую x(t), y(t)
        """
        if not self.x_func or not self.y_func:
            print("⚠️ x_func или y_func не установлены!")
            return

        print(f"\n🎨 === РИСУЕМ ПАРАМЕТРИЧЕСКУЮ КРИВУЮ ===")
        print(f"   Диапазон параметра t: [{self.t_min:.2f}, {self.t_max:.2f}]")
        print(f"   Видимая область X: [{self.x_min:.2f}, {self.x_max:.2f}]")
        print(f"   Видимая область Y: [{self.y_min:.2f}, {self.y_max:.2f}]")

        with self.canvas:
            Color(0, 0.5, 1, 1)  # голубой
            points = []

            num_points = 2000
            valid_points = 0

            for i in range(num_points + 1):
                t = self.t_min + (i / num_points) * (self.t_max - self.t_min)
                try:
                    x = self.x_func(t)
                    y = self.y_func(t)

                    if i == 0:
                        print(f"   Первая точка: t={t:.2f} → x={x:.2f}, y={y:.2f}")

                    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                        if not (math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y)):
                            # Стандартное масштабирование
                            screen_x = self._x_to_screen(x, area_x, area_size)
                            screen_y = self._y_to_screen(y, area_y, area_size)

                            if i == 0:
                                print(f"   На экране: screen_x={screen_x:.1f}, screen_y={screen_y:.1f}")

                            # Проверяем что точка в видимой области
                            if (area_x <= screen_x <= area_x + area_size and
                                area_y <= screen_y <= area_y + area_size):
                                points.extend([screen_x, screen_y])
                                valid_points += 1
                except Exception as e:
                    if i == 0:
                        print(f"   ❌ Ошибка в первой точке: {e}")
                    continue

            print(f"   ✅ Найдено {valid_points} валидных точек из {num_points}")

            if len(points) >= 4:
                Line(points=points, width=2.5, cap='round', joint='round')
                print(f"   ✅ Кривая нарисована ({len(points)//2} точек)")
            else:
                print(f"   ⚠️ Недостаточно точек для отрисовки!")
                print(f"   Возможно, кривая вне видимой области [{self.x_min}, {self.x_max}] × [{self.y_min}, {self.y_max}]")

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
        """
        Рисует оси координат с подписями
        """
        # Ось X (где y=0)
        screen_y = self._y_to_screen(0, area_y, area_size)
        if area_y <= screen_y <= area_y + area_size:
            Line(points=[area_x, screen_y, area_x + area_size, screen_y], width=1.5)
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
            arrow_size = 8
            Line(points=[
                screen_x - arrow_size/2, area_y + area_size - arrow_size,
                screen_x, area_y + area_size,
                screen_x + arrow_size/2, area_y + area_size - arrow_size
            ], width=1.5)

        self._draw_axis_labels(area_x, area_y, area_size, area_height)

    def _draw_axis_labels(self, area_x, area_y, area_size, area_height):
        """
        Рисует текстовые подписи рядом с осями координат
        """
        font_size = dp(12)
        label_color = (0.2, 0.2, 0.2, 1)

        # === Подписи на оси X ===
        x_unit_step = self._nice_number((self.x_max - self.x_min) / 8)
        x_start = math.ceil(self.x_min / x_unit_step) * x_unit_step
        x_end = math.floor(self.x_max / x_unit_step) * x_unit_step
        x = x_start
        while x <= x_end + x_unit_step / 100:
            if abs(x) > 0.01:
                screen_x = self._x_to_screen(x, area_x, area_size)
                screen_y_axis_x = self._y_to_screen(0, area_y, area_size)

                if area_x <= screen_x <= area_x + area_size and area_y <= screen_y_axis_x <= area_y + area_size:
                    label = CoreLabel(
                        text=str(round(x, 2)),
                        font_size=font_size,
                        color=label_color
                    )
                    label.refresh()
                    texture = label.texture
                    label_x = screen_x - texture.width / 2
                    label_y = screen_y_axis_x - texture.height - dp(3)
                    if label_y >= area_y - texture.height - dp(10):
                        Color(*label_color)
                        Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
            x += x_unit_step

        # === Подписи на оси Y ===
        y_unit_step = self._nice_number((self.y_max - self.y_min) / 8)
        y_start = math.ceil(self.y_min / y_unit_step) * y_unit_step
        y_end = math.floor(self.y_max / y_unit_step) * y_unit_step
        y = y_start
        while y <= y_end + y_unit_step / 100:
            if abs(y) > 0.01:
                screen_y = self._y_to_screen(y, area_y, area_size)
                screen_x_axis_y = self._x_to_screen(0, area_x, area_size)

                if area_y <= screen_y <= area_y + area_size and area_x <= screen_x_axis_y <= area_x + area_size:
                    label = CoreLabel(
                        text=str(round(y, 2)),
                        font_size=font_size,
                        color=label_color
                    )
                    label.refresh()
                    texture = label.texture
                    label_x = screen_x_axis_y - texture.width - dp(5)
                    label_y = screen_y - texture.height / 2
                    if label_x >= area_x - texture.width - dp(10):
                        Color(*label_color)
                        Rectangle(texture=texture, pos=(label_x, label_y), size=texture.size)
            y += y_unit_step

    def _draw_function(self, area_x, area_y, area_size, area_height):
        if not self.functions:
            return

        colors = [(0, 0, 1), (1, 0, 0)]

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
            Color(0, 0, 0)
            for x, y in self.intersection_points:
                screen_x = self._x_to_screen(x, area_x, area_size)
                screen_y = self._y_to_screen(y, area_y, area_size)
                if area_x <= screen_x <= area_x + area_size and area_y <= screen_y <= area_y + area_size:
                    Ellipse(pos=(screen_x - 4, screen_y - 4), size=(8, 8))

    def _x_to_screen(self, x, area_x, area_size):
        return area_x + ((x - self.x_min) / (self.x_max - self.x_min)) * area_size

    def _y_to_screen(self, y, area_y, area_size):
        normalized_y = (y - self.y_min) / (self.y_max - self.y_min)
        return area_y + normalized_y * area_size
