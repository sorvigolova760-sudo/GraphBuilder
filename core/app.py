"""
Основной класс приложения GraphBuilder
"""
import os
import re
from kivy.config import Config
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from parsers.function_parser import FunctionParser
from parsers.parametric_parser import ParametricParser
from ui.layout import build_ui
from ui.widgets.graph_widget import GraphWidget
from analyzers.standard_analyzer import StandardAnalyzer
from utils.intersection_finder import find_intersections
from utils.android_patch import apply_android_patch


class GraphFunctionApp(MDApp):
    """
    Основной класс приложения для построения и анализа графиков функций.
    Поддерживает как обычные функции y=f(x), так и параметрические кривые x=x(t), y=y(t).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Инициализация атрибутов, которые будут связаны с UI элементами
        self.func_input1 = None
        self.func_input2 = None
        self.param_mode_switch = None
        self.graph = None
        self.content_layout = None
        self.t_range_card = None
        self.t_min_input = None
        self.t_max_input = None
        self.x_min_input = None
        self.x_max_input = None
        self.y_min_input = None
        self.y_max_input = None
        self._current_params = []

    def build(self):
        """
        Метод для построения пользовательского интерфейса.
        """
        # Настройка темы
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Light"

        # Построение UI
        layout = build_ui(self)

        # Сброс после загрузки
        Clock.schedule_once(lambda dt: self.reset_function(), 0.5)

        return layout

    def toggle_param_mode(self, instance, value):
        """
        Переключение между обычным и параметрическим режимами.
        """
        is_param = value

        print(f"\n🔄 Переключение режима: {'ПАРАМЕТРИЧЕСКИЙ' if is_param else 'ОБЫЧНЫЙ'}")

        if is_param:
            # === ПАРАМЕТРИЧЕСКИЙ РЕЖИМ ===
            self.func_input1.hint_text = "x(t)"
            self.func_input2.hint_text = "y(t)"

            # Показываем карточку с диапазоном t
            if self.t_range_card not in self.content_layout.children:
                try:
                    func2_card = self.func_input2.parent
                    children_list = list(self.content_layout.children)
                    func2_index = len(children_list) - 1 - children_list.index(func2_card)
                    self.content_layout.add_widget(self.t_range_card, index=func2_index)
                    print("   ✅ Карточка t_range добавлена")
                except (ValueError, AttributeError) as e:
                    self.content_layout.add_widget(self.t_range_card)
                    print(f"   ⚠️ Карточка добавлена в конец: {e}")

            # Удаляем карточку с параметрами (a, b, c и т.д.), если она есть
            if hasattr(self, 'param_card') and self.param_card in self.content_layout.children:
                self.content_layout.remove_widget(self.param_card)
                print("   ✅ Карточка параметров удалена")

        else:
            # === ОБЫЧНЫЙ РЕЖИМ ===
            self.func_input1.hint_text = "Введите функцию 1"
            self.func_input2.hint_text = "Введите функцию 2"

            # Скрываем карточку с диапазоном t
            if self.t_range_card in self.content_layout.children:
                self.content_layout.remove_widget(self.t_range_card)
                print("   ✅ Карточка t_range удалена")

    def plot_function(self, *args):
        """
        Основной метод для построения графика.
        """
        try:
            is_param = self.param_mode_switch.active

            print(f"\n{'='*60}")
            print(f"🚀 ПОСТРОЕНИЕ ГРАФИКА: {'ПАРАМЕТРИЧЕСКИЙ' if is_param else 'ОБЫЧНЫЙ'} РЕЖИМ")
            print(f"{'='*60}")

            if is_param:
                # === ПАРАМЕТРИЧЕСКИЙ РЕЖИМ ===
                self._plot_parametric()
            else:
                # === ОБЫЧНЫЙ РЕЖИМ ===
                self._plot_standard()

        except Exception as e:
            print(f"✗ Ошибка построения: {e}")
            import traceback
            traceback.print_exc()

    def _plot_parametric(self):
        """
        Построение параметрической кривой.
        """
        x_expr = self.func_input1.text.strip()
        y_expr = self.func_input2.text.strip()

        if not x_expr or not y_expr:
            print("⚠️ Пустые выражения для параметрических функций")
            return

        print(f"   x(t) = {x_expr}")
        print(f"   y(t) = {y_expr}")

        # Получаем диапазон параметра t
        t_min = float(self.t_min_input.text)
        t_max = float(self.t_max_input.text)
        print(f"   Диапазон параметра t: [{t_min}, {t_max}]")

        # Получаем ВИДИМУЮ ОБЛАСТЬ (не путаем с диапазоном t!)
        x_min = float(self.x_min_input.text)
        x_max = float(self.x_max_input.text)
        y_min = float(self.y_min_input.text)
        y_max = float(self.y_max_input.text)
        print(f"   Видимая область: X ∈ [{x_min}, {x_max}], Y ∈ [{y_min}, {y_max}]")

        # Проверяем, есть ли параметры (a, b, c) в выражениях
        params = set()
        params.update(self.extract_parameters(x_expr))
        params.update(self.extract_parameters(y_expr))

        if params:
            print(f"   ⚠️ Найдены параметры: {params}")
            print(f"   Параметрические функции не должны содержать параметры кроме 't'!")

        # Парсим функции
        x_func, y_func = ParametricParser.parse(x_expr, y_expr)

        # Тестируем функции
        print(f"\n   Тест функций:")
        for t_test in [t_min, (t_min + t_max)/2, t_max]:
            x_val = x_func(t_test)
            y_val = y_func(t_test)
            print(f"     t={t_test:.2f} → x={x_val:.2f}, y={y_val:.2f}")

        # Устанавливаем параметрическую функцию
        self.graph.set_parametric(x_func, y_func, t_min, t_max)
        self.graph.set_ranges(x_min, x_max, y_min, y_max)
        self.graph.draw()

        print(f"   ✅ График построен")

        # Скрываем карточки, не относящиеся к параметрическому режиму
        for card_name in ['param_card', 'intersection_card', 'analysis_card']:
            if hasattr(self, card_name):
                if getattr(self, card_name) in self.content_layout.children:
                    self.content_layout.remove_widget(getattr(self, card_name))
                delattr(self, card_name)

    def _plot_standard(self):
        """
        Построение обычных функций f(x) и g(x).
        """
        expr1 = self.func_input1.text.strip()
        expr2 = self.func_input2.text.strip()

        funcs = []
        all_params = set()

        # Обрабатываем первую функцию
        if expr1:
            params1 = self.extract_parameters(expr1)
            all_params.update(params1)
            print(f"   Функция 1: {expr1}, параметры: {params1}")

        # Обрабатываем вторую функцию
        if expr2:
            params2 = self.extract_parameters(expr2)
            all_params.update(params2)
            print(f"   Функция 2: {expr2}, параметры: {params2}")

        # --- НОВАЯ ЛОГИКА ---
        # Если в новых выражениях нет параметров, но карточка параметров существует, удаляем её
        if not all_params and hasattr(self, 'param_card') and self.param_card in self.content_layout.children:
            print("   Удаление карточки параметров: параметры отсутствуют в новых выражениях.")
            self.content_layout.remove_widget(self.param_card)
            delattr(self, 'param_card')
            # Также удаляем сами слайдеры и метки, если они были
            attrs_to_remove = [attr for attr in dir(self) if attr.endswith('_slider') or attr.endswith('_label')]
            for attr in attrs_to_remove:
                if hasattr(self, attr):
                    delattr(self, attr)
            if hasattr(self, '_current_params'):
                delattr(self, '_current_params')


        # Обновляем слайдеры для параметров (если они есть)
        if all_params:
            print(f"   Все параметры: {all_params}")
            if not hasattr(self, '_current_params') or set(self._current_params) != all_params:
                # Удаляем старую карточку, если она существует (например, с прошлого раза)
                if hasattr(self, 'param_card') and self.param_card in self.content_layout.children:
                    self.content_layout.remove_widget(self.param_card)
                self._current_params = list(all_params)
                self.update_parameter_sliders(self._current_params)
                # После создания слайдеров сразу строим график
                self._rebuild_graph_with_current_params()
                return

        # Если дошли до этого места, значит параметров не было или они не изменились
        # Подставляем значения параметров и строим график
        self._rebuild_graph_with_current_params()

    def _rebuild_graph_with_current_params(self):
        """
        Перестраивает график с текущими параметрами из ОБЕИХ функций.
        """
        expr1 = self.func_input1.text.strip()
        expr2 = self.func_input2.text.strip()

        if not expr1 and not expr2:
            return

        # Собираем все параметры
        all_params = set()
        if expr1:
            all_params.update(self.extract_parameters(expr1))
        if expr2:
            all_params.update(self.extract_parameters(expr2))

        # Подставляем значения параметров
        final_funcs = []
        for expr in [expr1, expr2]:
            if not expr:
                continue
            expr_with_values = expr
            for p in all_params:
                if hasattr(self, f"{p}_slider"):
                    val = getattr(self, f"{p}_slider").value
                    val_rounded = round(val * 2) / 2
                    expr_with_values = re.sub(rf'\b{p}\b', str(val_rounded), expr_with_values)
            parser = FunctionParser()
            final_funcs.append(parser.parse(expr_with_values))

        if not final_funcs:
            return

        # Получаем ВИДИМУЮ ОБЛАСТЬ из полей ввода
        x_min = float(self.x_min_input.text)
        x_max = float(self.x_max_input.text)
        y_min = float(self.y_min_input.text)
        y_max = float(self.y_max_input.text)

        print(f"   Диапазоны: X=[{x_min}, {x_max}], Y=[{y_min}, {y_max}]")

        self.graph.set_functions(final_funcs)
        self.graph.set_ranges(x_min, x_max, y_min, y_max)

        # Пересечения
        intersections = []
        if len(final_funcs) == 2:
            intersections = find_intersections(final_funcs[0], final_funcs[1], x_min, x_max)
        self.graph.intersection_points = intersections

        self.graph.draw()
        self._show_intersection_card(intersections)

    def reset_function(self, *args):
        """
        Сброс всех полей и графика.
        """
        print("\n🔄 СБРОС")

        self.func_input1.text = ""
        self.func_input2.text = ""
        self.x_min_input.text = "-5"
        self.x_max_input.text = "5"
        self.y_min_input.text = "-5"
        self.y_max_input.text = "5"
        self.t_min_input.text = "0"
        self.t_max_input.text = "6.28"

        # Отключаем параметрический режим
        self.param_mode_switch.active = False

        # Очищаем график
        self.graph.set_functions([])
        self.graph.is_parametric = False
        self.graph.x_func = None
        self.graph.y_func = None
        self.graph.draw()

        # Удаляем карточки
        for attr_name in ['param_card', 'intersection_card', 'analysis_card']:
            if hasattr(self, attr_name):
                card = getattr(self, attr_name)
                if card in self.content_layout.children:
                    self.content_layout.remove_widget(card)
                delattr(self, attr_name)

        # Скрываем карточку t_range
        if hasattr(self, 't_range_card') and self.t_range_card in self.content_layout.children:
            self.content_layout.remove_widget(self.t_range_card)

        # Удаляем все слайдеры и метки
        attrs_to_remove = [attr for attr in dir(self) if attr.endswith('_slider') or attr.endswith('_label')]
        for attr in attrs_to_remove:
            delattr(self, attr)

        if hasattr(self, '_current_params'):
            delattr(self, '_current_params')

        print("   ✅ Сброс выполнен")

    def analyze_function(self, *args):
        """
        Анализирует ПЕРВУЮ функцию.
        """
        try:
            expr = self.func_input1.text.strip()
            if not expr:
                return

            x_min = float(self.x_min_input.text)
            x_max = float(self.x_max_input.text)

            parser = FunctionParser()
            func = parser.parse(expr)

            analyzer = StandardAnalyzer(func, expr, x_min, x_max)
            analysis_text = analyzer.to_text()

            if hasattr(self, 'analysis_card'):
                self.content_layout.remove_widget(self.analysis_card)

            self.analysis_card = MDCard(
                orientation="vertical",
                padding=dp(15),
                size_hint=(1, None),
                height=dp(350),
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
                height=dp(310)
            )
            self.analysis_card.add_widget(label)
            self.content_layout.add_widget(self.analysis_card)

        except Exception as e:
            print(f"Ошибка анализа: {e}")
            import traceback
            traceback.print_exc()

    def save_screenshot(self, *args):
        """
        Сохраняет график как PNG.
        """
        try:
            import os
            from kivy.utils import platform

            if platform == 'android':
                from android.storage import app_storage_path # pyright: ignore[reportMissingImports]
                from jnius import autoclass # pyright: ignore[reportMissingImports]
                Environment = autoclass('android.os.Environment')
                dir_path = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                ).toString()
            else:
                dir_path = os.path.expanduser("~/Downloads")

            os.makedirs(dir_path, exist_ok=True)

            filename = "graph_plot.png"
            full_path = os.path.join(dir_path, filename)

            self.graph.export_to_png(full_path)

            if platform != 'linux':
                from kivymd.toast import toast
                toast(f"Скриншот сохранён:\n{filename}")
            else:
                print(f"✅ Скриншот сохранён: {full_path}")

        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            import traceback
            traceback.print_exc()

    def extract_parameters(self, expr):
        """
        Извлекает параметры из выражения (все буквы, кроме x, t и функций).
        """
        # Удаляем известные функции
        func_free = re.sub(
            r'\b(sin|cos|tan|asin|acos|atan|sqrt|log|exp|abs|pi|e)\b',
            '',
            expr.lower()
        )
        # Находим все одиночные буквы (кроме 'x' и 't')
        params = set(re.findall(r'\b([a-su-wyz])\b', func_free))  # исключили 't'
        return sorted(params)

    def update_parameter_sliders(self, params):
        """
        Создаёт слайдеры для параметров функции (не путать с параметром t!).
        """
        # Удаляем старую карточку
        if hasattr(self, 'param_card'):
            if self.param_card in self.content_layout.children:
                self.content_layout.remove_widget(self.param_card)

        if not params:
            return

        print(f"   Создаём слайдеры для параметров: {params}")

        # Создаём новую карточку
        self.param_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(40 + len(params) * 60),
            elevation=2,
            radius=[10]
        )

        title = MDLabel(text="Параметры функции:", role="medium", size_hint=(1, None), height=dp(30))
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
                step=1,
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

        # Вставляем сразу после графика
        graph_card = self.graph.parent
        try:
            children_list = list(self.content_layout.children)
            graph_index = len(children_list) - 1 - children_list.index(graph_card)
            self.content_layout.add_widget(self.param_card, index=graph_index)
        except (ValueError, AttributeError):
            self.content_layout.add_widget(self.param_card)

    def _show_intersection_card(self, intersections):
        """
        Показывает карточку с точками пересечения.
        """
        if hasattr(self, 'intersection_card'):
            if self.intersection_card in self.content_layout.children:
                self.content_layout.remove_widget(self.intersection_card)

        if not intersections:
            return

        lines = ["Точки пересечения:"]
        for x, y in intersections:
            lines.append(f"• ({x:.2f}, {y:.2f})")
        text = "\n".join(lines)

        self.intersection_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(40 + len(intersections) * 30),
            elevation=2,
            radius=[10]
        )
        label = MDLabel(
            text=text,
            halign="left",
            font_size="14sp",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(20 + len(intersections) * 30)
        )
        self.intersection_card.add_widget(label)

        graph_card = self.graph.parent
        try:
            children_list = list(self.content_layout.children)
            graph_index = len(children_list) - 1 - children_list.index(graph_card)
            self.content_layout.add_widget(self.intersection_card, index=graph_index)
        except (ValueError, AttributeError):
            self.content_layout.add_widget(self.intersection_card)

    def _on_slider_change(self, param_name, label, value):
        """
        Обработчик изменения слайдера параметра.
        """
        rounded_value = round(value * 2) / 2
        label.text = f"{param_name} = {rounded_value:.1f}"
        # Перестраиваем график с новыми значениями параметров
        self._rebuild_graph_with_current_params()

    def set_example(self, expr, ranges):
        """
        Устанавливает пример функции.
        """
        self.func_input1.text = expr
        self.func_input2.text = ""  # очищаем вторую функцию
        self.x_min_input.text = str(ranges[0])
        self.x_max_input.text = str(ranges[1])
        self.y_min_input.text = str(ranges[2])
        self.y_max_input.text = str(ranges[3])
        self.plot_function()
