# ui_layout.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton
from kivymd.uix.button.button import MDButtonText
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from graph_widget import GraphWidget

def build_ui(app_instance):
    root_layout = MDBoxLayout(
        orientation="vertical",
        padding=dp(10),
        spacing=dp(10)
    )

    # === ЗАГОЛОВОК ===
    title = MDLabel(
        text="Построитель графиков функций",
        halign="center",
        role="large",  # ← ИСПРАВЛЕНО: вместо font_style="H5"
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

    # === Верхняя панель: ввод и кнопки ===
    input_card = MDCard(
        orientation="vertical",
        padding=dp(12),
        size_hint=(1, None),
        height=dp(160),
        elevation=2
    )

    # --- Строка 1: поле ввода ---
    # --- Строка 1a: первое поле ввода ---
    input_row1a = MDBoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(45),
        padding=[0, 0, 0, dp(4)]
    )
    app_instance.func_input1 = MDTextField(
        text="x**2",
        hint_text="Функция 1",
        mode="filled",
        font_size='14sp'
    )
    input_row1a.add_widget(app_instance.func_input1)
    input_card.add_widget(input_row1a)

    # --- Строка 1b: второе поле ввода ---
    input_row1b = MDBoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(45),
        padding=[0, 0, 0, dp(4)]
    )
    app_instance.func_input2 = MDTextField(
        text="x+2",
        hint_text="Функция 2",
        mode="filled",
        font_size='14sp'
    )
    input_row1b.add_widget(app_instance.func_input2)
    input_card.add_widget(input_row1b)

    # --- Строка 2: четыре кнопки ---
    input_row2 = MDBoxLayout(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(45),
        spacing=dp(4)
    )

    plot_btn = MDButton(
        MDButtonText(text="График", font_size="18sp"),
        style="filled",
        size_hint=(0.28, None),
        height=dp(45),
        on_release=app_instance.plot_function
    )

    reset_btn = MDButton(
        MDButtonText(text="Сброс", font_size="18sp"),
        style="filled",
        size_hint=(0.24, None),
        height=dp(45),
        on_release=app_instance.reset_function,
        md_bg_color=(0.3, 0.6, 0.3, 1)
    )

    analyze_btn = MDButton(
        MDButtonText(text="Анализ", font_size="18sp"),
        style="filled",
        size_hint=(0.24, None),
        height=dp(45),
        on_release=app_instance.analyze_function,
        md_bg_color=(0.2, 0.6, 0.8, 1)
    )

    screenshot_btn = MDButton(
        MDButtonText(text="Фото", font_size="18sp"),
        style="filled",
        size_hint=(0.24, None),
        height=dp(45),
        on_release=app_instance.save_screenshot,
        md_bg_color=(0.5, 0.5, 0.5, 1)
    )

    input_row2.add_widget(plot_btn)
    input_row2.add_widget(reset_btn)
    input_row2.add_widget(analyze_btn)
    input_row2.add_widget(screenshot_btn)
    input_card.add_widget(input_row2)
    content.add_widget(input_card)

    # === График ===
    graph_card = MDCard(
        padding=dp(10),
        size_hint=(1, None),
        height=dp(400),
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
        role="medium",  # ← ИСПРАВЛЕНО: вместо font_style="Subtitle1"
        size_hint=(1, None),
        height=dp(30)
    )
    control_card.add_widget(control_title)
    range_grid = MDGridLayout(cols=4, spacing=dp(10), size_hint=(1, None), height=dp(50))
    app_instance.x_min_input = MDTextField(text="-5", hint_text="X min", mode="outlined", input_filter="float")
    app_instance.x_max_input = MDTextField(text="5", hint_text="X max", mode="outlined", input_filter="float")
    app_instance.y_min_input = MDTextField(text="-5", hint_text="Y min", mode="outlined", input_filter="float")
    app_instance.y_max_input = MDTextField(text="5", hint_text="Y max", mode="outlined", input_filter="float")
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
        role="medium",  # ← ИСПРАВЛЕНО
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
        btn = MDButton(
            MDButtonText(text=name, font_size="14sp"),
            style="text",
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda inst, e=expr, r=ranges: app_instance.set_example(e, r)
        )
        examples_grid.add_widget(btn)
    examples_card.add_widget(examples_grid)
    content.add_widget(examples_card)

    scroll_view.add_widget(content)
    root_layout.add_widget(scroll_view)
    return root_layout