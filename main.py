# main.py
import os
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['KIVY_WINDOW'] = 'sdl2'
from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

from kivymd.app import MDApp
from kivy.clock import Clock
import math
from function_parser import FunctionParser
from ui_layout import build_ui
from kivy.core.text import Label as CoreLabel

class GraphFunctionApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Light"
        layout = build_ui(self)
        Clock.schedule_once(lambda dt: self.plot_function(), 0.5)
        return layout

    def plot_function(self, *args):
        try:
            expr = self.func_input.text.strip()
            if not expr:
                return
            parser = FunctionParser()
            func = parser.parse(expr)
            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)
            y_min = float(self.y_min_input.text)
            y_max = float(self.y_max_input.text)
            if x_min >= x_max or y_min >= y_max:
                print("Ошибка: некорректные диапазоны")
                return
            print(f"\n{'='*60}")
            print(f"ФУНКЦИЯ: {expr}")
            print(f"Диапазон: X=[{x_min:.2f}, {x_max:.2f}], Y=[{y_min:.2f}, {y_max:.2f}]")
            print(f"{'='*60}")
            if 'sin' in expr.lower():
                test_result = func(0)
                if math.isnan(test_result):
                    print(f"  ⚠️ ВНИМАНИЕ: sin(0) вернул NaN! Проблема в парсере!")
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

    def reset_function(self, *args):
        """Сбрасывает всё к начальному состоянию"""
        self.func_input.text = ""  # Очищаем поле ввода
        self.x_min_input.text = "-5"
        self.x_max_input.text = "5"
        self.y_min_input.text = "-5"
        self.y_max_input.text = "5"
        self.graph.set_function(None)  # Убираем функцию → график исчезнет
        self.graph.draw()  # Перерисовываем пустой график

    def set_example(self, expr, ranges):
        self.func_input.text = expr
        self.x_min_input.text = str(ranges[0])
        self.x_max_input.text = str(ranges[1])
        self.y_min_input.text = str(ranges[2])
        self.y_max_input.text = str(ranges[3])
        self.plot_function()

if __name__ == '__main__':
    GraphFunctionApp().run()