# main.py
# ========== ANDROID PATCH ==========
import sys

# Патч для Python 3.11+ на Android
if 'collections' in sys.modules:
    import collections.abc
    import collections
    collections.Mapping = collections.abc.Mapping
    collections.Sequence = collections.abc.Sequence
    sys.modules['collections'] = collections
    print("✅ Android collections patch applied")
# ===================================

import os
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_WINDOW'] = 'sdl2'
from kivy.config import Config
Config.set('graphics', 'multisamples', '16')
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

from kivymd.app import MDApp
from kivy.clock import Clock
import math
from function_parser import FunctionParser
from ui_layout import build_ui
from kivy.core.text import Label as CoreLabel
# Импорты для параметров
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.metrics import dp
import re

class GraphFunctionApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Light"  # ← Установим светлую тему
        layout = build_ui(self)
        Clock.schedule_once(lambda dt: self.plot_function(), 0.5)
        return layout

    def plot_function(self, *args):
        try:
            expr1 = self.func_input1.text.strip()
            expr2 = self.func_input2.text.strip()

            # Парсим вторую функцию (если есть)
            funcs = []
            func2 = None
            if expr2:
                parser2 = FunctionParser()
                func2 = parser2.parse(expr2)
                funcs.append(func2)

            # === РАБОТА С ПЕРВОЙ ФУНКЦИЕЙ И ПАРАМЕТРАМИ ===
            if expr1:
                # Извлекаем параметры
                params = self.extract_parameters(expr1)
            
                # Создаём/обновляем слайдеры
                if not hasattr(self, '_current_params') or set(self._current_params) != set(params):
                    self._current_params = params
                    self.update_parameter_sliders(params)
                    # После создания слайдеров — перестраиваем график
                    self._rebuild_graph_with_current_params()
                    return  # ← ВАЖНО: выходим, чтобы не дублировать построение
                else:
                    # Слайдеры уже есть — строим с их значениями
                    param_values = {}
                    for p in params:
                        if hasattr(self, f"{p}_slider"):
                            raw_value = getattr(self, f"{p}_slider").value
                            param_values[p] = round(raw_value * 2) / 2
                        else:
                            param_values[p] = 1.0

                    expr1_with_values = expr1
                    for p, val in param_values.items():
                        expr1_with_values = re.sub(rf'\b{p}\b', str(val), expr1_with_values)

                    parser1 = FunctionParser()
                    func1 = parser1.parse(expr1_with_values)
                    funcs.insert(0, func1)  # Первая функция — в начало списка
            else:
                # Удаляем слайдеры
                if hasattr(self, 'param_card'):
                    self.content_layout.remove_widget(self.param_card)
                    delattr(self, 'param_card')
                if hasattr(self, '_current_params'):
                    delattr(self, '_current_params')

            if not funcs:
                return

            # Устанавливаем функции и диапазоны
            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)
            y_min = float(self.y_min_input.text)
            y_max = float(self.y_max_input.text)

            self.graph.set_functions(funcs)
            self.graph.set_ranges(x_min, x_max, y_min, y_max)

            # Пересечения
            if len(funcs) == 2 and expr1 and expr2:
                intersections = self.find_intersections(funcs[0], funcs[1], x_min, x_max)
                self.graph.intersection_points = intersections
                print(f"Точки пересечения: {intersections}")
            else:
                self.graph.intersection_points = []

            self.graph.draw()

        except Exception as e:
            print(f"✗ Ошибка построения: {e}")
            import traceback
            traceback.print_exc()
    
    def find_intersections(self, f1, f2, x_min, x_max, tolerance=1e-6):
        """Находит точки пересечения двух функций численно"""
        intersections = []
        step = (x_max - x_min) / 500  # достаточно плотно

        for i in range(500):
            x1 = x_min + i * step
            x2 = x1 + step
            try:
                y1_1 = f1(x1)
                y1_2 = f2(x1)
                y2_1 = f1(x2)
                y2_2 = f2(x2)

                diff1 = y1_1 - y1_2
                diff2 = y2_1 - y2_2

                # Если разность сменила знак — есть корень
                if diff1 * diff2 < 0:
                    root = self.bisection_intersection(f1, f2, x1, x2, tolerance)
                    if root is not None:
                        y_val = f1(root)
                        intersections.append((root, y_val))
            except:
                continue

        # Убираем дубликаты
        unique = []
        for x, y in intersections:
            if not any(abs(x - ux) < 0.1 for ux, uy in unique):
                unique.append((x, y))
        return unique

    def bisection_intersection(self, f1, f2, a, b, tol=1e-6, max_iter=50):
        """Бисекция для f1(x) - f2(x) = 0"""
        try:
            fa = f1(a) - f2(a)
            fb = f1(b) - f2(b)
            if fa * fb > 0:
                return None

            for _ in range(max_iter):
                c = (a + b) / 2
                fc = f1(c) - f2(c)
                if abs(fc) < tol:
                    return c
                if fa * fc < 0:
                    b, fb = c, fc
                else:
                    a, fa = c, fc
            return (a + b) / 2
        except:
            return None

    def reset_function(self, *args):
        # Сбрасываем оба поля ввода
        self.func_input1.text = ""
        self.func_input2.text = ""
    
        # Сбрасываем диапазоны
        self.x_min_input.text = "-5"
        self.x_max_input.text = "5"
        self.y_min_input.text = "-5"
        self.y_max_input.text = "5"
    
        # Очищаем график
        self.graph.set_functions([])
        self.graph.draw()
    
        # Удаляем карточку параметров (если есть)
        if hasattr(self, 'param_card'):
            self.content_layout.remove_widget(self.param_card)
            delattr(self, 'param_card')
    
        # Удаляем все атрибуты слайдеров
        attrs_to_remove = []
        for attr in dir(self):
            if attr.endswith('_slider') or attr.endswith('_label'):
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            delattr(self, attr)
    
        # Сбрасываем текущие параметры
        if hasattr(self, '_current_params'):
            delattr(self, '_current_params')

    def analyze_function(self, *args):
        """Анализирует ПЕРВУЮ функцию"""
        try:
            expr = self.func_input1.text.strip()  # ← Берём ТОЛЬКО первую
            if not expr:
                return

            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)

            parser = FunctionParser()
            func = parser.parse(expr)

            from function_analyzer import FunctionAnalyzer
            analyzer = FunctionAnalyzer(func, expr, x_min, x_max)
            analysis_text = analyzer.to_text()

            # Удаляем старую карточку
            if hasattr(self, 'analysis_card'):
                self.content_layout.remove_widget(self.analysis_card)

            from kivymd.uix.card import MDCard
            from kivymd.uix.label import MDLabel
            from kivy.metrics import dp

            self.analysis_card = MDCard(
                orientation="vertical",
                padding=dp(15),
                size_hint=(1, None),
                height=dp(300),
                elevation=2,
                radius=[10]
            )
            label = MDLabel(
                text=analysis_text,
                halign="left",
                valign="top",
                font_size="14sp",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(280)
            )
            self.analysis_card.add_widget(label)
            self.content_layout.add_widget(self.analysis_card)

        except Exception as e:
            print(f"Ошибка анализа: {e}")
            import traceback
            traceback.print_exc()

    def save_screenshot(self, *args):
        """Сохраняет график как PNG"""
        try:
            import os
            from kivy.utils import platform

            if platform == 'android':
                # Импортируем только на Android
                from android.storage import app_storage_path
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                dir_path = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                ).toString()
            else:
                # На ПК сохраняем в ~/Downloads
                dir_path = os.path.expanduser("~/Downloads")

            # Убедимся, что папка существует
            os.makedirs(dir_path, exist_ok=True)

            filename = "graph_plot.png"
            full_path = os.path.join(dir_path, filename)

            # Экспортируем график
            self.graph.export_to_png(full_path)

            # Уведомление (только если не Linux)
            if platform != 'linux':
                from kivymd.toast import toast
                toast(f"Скриншот сохранён:\n{filename}")
            else:
                print(f"✅ Скриншот сохранён: {full_path}")

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            import traceback
            traceback.print_exc()
            # Для Linux — просто выводим сообщение
            if platform == 'linux':
                print("⚠️ Toast не поддерживается на Linux")
            else:
                from kivymd.toast import toast
                toast("Ошибка сохранения скриншота")

    def extract_parameters(self, expr):
        """Извлекает параметры из выражения (все буквы, кроме x и функций)"""
        # Удаляем известные функции
        func_free = re.sub(
            r'\b(sin|cos|tan|asin|acos|atan|sqrt|log|exp|abs|pi|e)\b', 
            '', 
            expr.lower()
        )
        # Находим все одиночные буквы (кроме 'x')
        params = set(re.findall(r'\b([a-wyz])\b', func_free))
        return sorted(params)

    def update_parameter_sliders(self, params):
        # Удаляем старую карточку
        if hasattr(self, 'param_card'):
            self.content_layout.remove_widget(self.param_card)

        if not params:
            return

        # Создаём новую карточку
        self.param_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(40 + len(params) * 60),
            elevation=2,
            radius=[10]
        )

        title = MDLabel(text="Параметры:", role="medium", size_hint=(1, None), height=dp(30))
        self.param_card.add_widget(title)

        for p in params:
            current_value = 1.0
            if hasattr(self, f"{p}_slider"):
                current_value = getattr(self, f"{p}_slider").value

            label = MDLabel(
                text=f"{p} = {current_value:.2f}",
                halign="left",
                size_hint=(1, None),
                height=dp(20)
            )
            setattr(self, f"{p}_label", label)

            slider = MDSlider(
                min=-10,
                max=10,
                value=current_value,
                step=1,  # ← ДОБАВЛЕНО
                size_hint=(1, None),
                height=dp(40)
            )

            slider.bind(
                value=lambda instance, value, param=p, lbl=label: 
                    self._on_slider_change(param, lbl, value)
            )
            setattr(self, f"{p}_slider", slider)

            self.param_card.add_widget(label)
            self.param_card.add_widget(slider)

        # === ВСТАВЛЯЕМ СРАЗУ ПОСЛЕ ГРАФИКА ===
        graph_card = self.graph.parent  # это MDCard, содержащий GraphWidget
        try:
            # children в обратном порядке, поэтому ищем с конца
            children_list = list(self.content_layout.children)
            graph_index = len(children_list) - 1 - children_list.index(graph_card)
            self.content_layout.add_widget(self.param_card, index=graph_index)
        except (ValueError, AttributeError):
            # Если не нашли — добавляем в конец
            self.content_layout.add_widget(self.param_card)

    def _on_slider_change(self, param_name, label, value):
        rounded_value = round(value * 2) / 2
        label.text = f"{param_name} = {rounded_value:.1f}"
        self._rebuild_graph_with_current_params()  # ← вызываем новый метод
    
    def _rebuild_graph_with_current_params(self):
        """Перестраивает график с текущими параметрами ПЕРВОЙ функции"""
        expr1 = self.func_input1.text.strip()
        expr2 = self.func_input2.text.strip()

        if not expr1:
            return

        # Обрабатываем первую функцию с параметрами
        params = self.extract_parameters(expr1)
        param_values = {}
        for p in params:
            if hasattr(self, f"{p}_slider"):
                raw_value = getattr(self, f"{p}_slider").value
                param_values[p] = round(raw_value * 2) / 2
            else:
                param_values[p] = 1.0

        expr1_with_values = expr1
        for p, val in param_values.items():
            expr1_with_values = re.sub(rf'\b{p}\b', str(val), expr1_with_values)

        parser1 = FunctionParser()
        func1 = parser1.parse(expr1_with_values)

        funcs = [func1]

        # Добавляем вторую функцию, если есть
        if expr2:
            parser2 = FunctionParser()
            func2 = parser2.parse(expr2)
            funcs.append(func2)

        # Пересечение
        if len(funcs) == 2:
            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)
            intersections = self.find_intersections(funcs[0], funcs[1], x_min, x_max)
            self.graph.intersection_points = intersections
        else:
            self.graph.intersection_points = []

        # Обновляем график
        x_min = float(self.x_min_input.text)
        x_max = float(self.x_max_input.text)
        y_min = float(self.y_min_input.text)
        y_max = float(self.y_max_input.text)

        self.graph.set_functions(funcs)
        self.graph.set_ranges(x_min, x_max, y_min, y_max)
        self.graph.draw()

    def set_example(self, expr, ranges):
        self.func_input.text = expr
        self.x_min_input.text = str(ranges[0])
        self.x_max_input.text = str(ranges[1])
        self.y_min_input.text = str(ranges[2])
        self.y_max_input.text = str(ranges[3])
        self.plot_function()

if __name__ == '__main__':
    GraphFunctionApp().run()