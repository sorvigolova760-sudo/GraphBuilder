# ui_layout.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from graph_widget import GraphWidget

def build_ui(app_instance):
    # Основной layout (заголовок + прокручиваемая область)
    root_layout = MDBoxLayout(
        orientation="vertical",
        padding=dp(10),
        spacing=dp(10)
    )

    # === ЗАГОЛОВОК (всегда виден) ===
    title = MDLabel(
        text="Построитель графиков функций",
        halign="center",
        font_style="H5",
        theme_text_color="Primary",
        size_hint=(1, None),
        height=dp(40)
    )
    root_layout.add_widget(title)

    # === ПРОКРУЧИВАЕМАЯ ОБЛАСТЬ ===
    scroll_view = ScrollView(
        do_scroll_x=False,
        bar_width=dp(4),
        bar_color=(0.6, 0.6, 0.6, 1),
        bar_inactive_color=(0.8, 0.8, 0.8, 1)
    )

    content = MDBoxLayout(
        orientation="vertical",
        padding=dp(0),
        spacing=dp(10),
        size_hint_y=None
    )
    content.bind(minimum_height=content.setter('height'))
    app_instance.content_layout = content

   # === Верхняя панель: ввод и кнопки (две строки) ===
    input_card = MDCard(
        orientation="vertical",
        padding=dp(12),  # чуть меньше отступы
        size_hint=(1, None),
        height=dp(110),  # немного выше из-за двух строк
        elevation=2
    )

    # --- Строка 1: только поле ввода ---
    input_row1 = MDBoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(45),
        padding=[0, 0, 0, dp(8)]  # отступ снизу
    )
    app_instance.func_input = MDTextField(
        text="x**2",
        hint_text="Введите функцию",
        mode="fill",
        font_size='14sp'
    )
    input_row1.add_widget(app_instance.func_input)
    input_card.add_widget(input_row1)

    # --- Строка 2: три кнопки в ряд ---
    input_row2 = MDBoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(45),
        spacing=dp(6)
    )

    plot_btn = MDRaisedButton(
        text="График",
        size_hint_x=0.33,
        height=dp(45),
        on_press=app_instance.plot_function,
        font_size='12sp'
    )

    reset_btn = MDRaisedButton(
        text="Сброс",
        size_hint_x=0.33,
        height=dp(45),
        on_press=app_instance.reset_function,
        md_bg_color=(0.3, 0.6, 0.3, 1),
        font_size='12sp'
    )

    analyze_btn = MDRaisedButton(
        text="Анализ",
        size_hint_x=0.34,
        height=dp(45),
        on_press=app_instance.analyze_function,
        md_bg_color=(0.2, 0.6, 0.8, 1),
        font_size='12sp'
    )

    input_row2.add_widget(plot_btn)
    input_row2.add_widget(reset_btn)
    input_row2.add_widget(analyze_btn)
    input_card.add_widget(input_row2)

    # Добавляем карточку в контент
    content.add_widget(input_card)

    # === График ===
    graph_card = MDCard(
        padding=dp(10),
        size_hint=(1, None),
        height=dp(400),  # Фиксированная высота для графика
        elevation=3,
        radius=[15, 15, 15, 15],
        md_bg_color=(0.95, 0.95, 0.95, 1)
    )
    app_instance.graph = GraphWidget()
    graph_card.add_widget(app_instance.graph)
    content.add_widget(graph_card)

    # === Управление диапазонами ===
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
    range_grid = MDGridLayout(cols=4, spacing=dp(10), size_hint=(1, None), height=dp(50))
    app_instance.x_min_input = MDTextField(text="-5", hint_text="X min", mode="rectangle", input_filter="float")
    app_instance.x_max_input = MDTextField(text="5", hint_text="X max", mode="rectangle", input_filter="float")
    app_instance.y_min_input = MDTextField(text="-5", hint_text="Y min", mode="rectangle", input_filter="float")
    app_instance.y_max_input = MDTextField(text="5", hint_text="Y max", mode="rectangle", input_filter="float")
    for widget in [app_instance.x_min_input, app_instance.x_max_input, app_instance.y_min_input, app_instance.y_max_input]:
        range_grid.add_widget(widget)
    control_card.add_widget(range_grid)
    content.add_widget(control_card)

    # === Примеры функций ===
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
            on_press=lambda inst, e=expr, r=ranges: app_instance.set_example(e, r)
        )
        examples_grid.add_widget(btn)
    examples_card.add_widget(examples_grid)
    content.add_widget(examples_card)

    # Добавляем контент в ScrollView
    scroll_view.add_widget(content)
    root_layout.add_widget(scroll_view)

    return root_layout