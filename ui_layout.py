# ui_layout.py (с поддержкой диапазона t для параметрических функций)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton
from kivymd.uix.button.button import MDButtonText
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
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
        role="large",
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

    # === Переключатель режима ===
    mode_card = MDCard(
        orientation="horizontal",
        padding=dp(12),
        size_hint=(1, None),
        height=dp(50),
        elevation=2
    )

    mode_label = MDLabel(
        text="Параметрический режим:",
        size_hint=(None, None),
        width=dp(180),
        height=dp(30)
    )
    mode_card.add_widget(mode_label)

    app_instance.param_mode_switch = MDSwitch(active=False)
    app_instance.param_mode_switch.bind(active=app_instance.toggle_param_mode)

    mode_card.add_widget(app_instance.param_mode_switch)

    content.add_widget(mode_card)

    # === Карточка для первой функции ===
    func1_card = MDCard(
        orientation="vertical",
        padding=dp(12),
        size_hint=(1, None),
        height=dp(90),
        elevation=2
    )
    title1 = MDLabel(
        text="Функция 1",
        role="small",
        size_hint=(1, None),
        height=dp(20)
    )
    func1_card.add_widget(title1)
    app_instance.func_input1 = MDTextField(
        text="x**2",
        hint_text="Введите функцию 1",
        mode="filled",
        font_size='14sp'
    )
    func1_card.add_widget(app_instance.func_input1)
    content.add_widget(func1_card)

    # === Карточка для второй функции ===
    func2_card = MDCard(
        orientation="vertical",
        padding=dp(12),
        size_hint=(1, None),
        height=dp(90),
        elevation=2
    )
    title2 = MDLabel(
        text="Функция 2",
        role="small",
        size_hint=(1, None),
        height=dp(20)
    )
    func2_card.add_widget(title2)
    app_instance.func_input2 = MDTextField(
        text="x+2",
        hint_text="Введите функцию 2",
        mode="filled",
        font_size='14sp'
    )
    func2_card.add_widget(app_instance.func_input2)
    content.add_widget(func2_card)

    # === НОВАЯ КАРТОЧКА: Диапазон параметра t (скрыта по умолчанию) ===
    app_instance.t_range_card = MDCard(
        orientation="vertical",
        padding=dp(15),
        size_hint=(1, None),
        height=dp(120),
        elevation=2
    )
    t_title = MDLabel(
        text="Диапазон параметра t:",
        role="medium",
        size_hint=(1, None),
        height=dp(30)
    )
    app_instance.t_range_card.add_widget(t_title)
    
    t_grid = MDGridLayout(cols=2, spacing=dp(10), size_hint=(1, None), height=dp(50))
    app_instance.t_min_input = MDTextField(text="0", hint_text="t min", mode="outlined", input_filter="float")
    app_instance.t_max_input = MDTextField(text="6.28", hint_text="t max", mode="outlined", input_filter="float")
    t_grid.add_widget(app_instance.t_min_input)
    t_grid.add_widget(app_instance.t_max_input)
    app_instance.t_range_card.add_widget(t_grid)
    
    # НЕ добавляем сразу, будем показывать только в параметрическом режиме

    # === Кнопки в карточке с горизонтальной прокруткой ===
    button_card = MDCard(
        padding=dp(5),
        size_hint=(1, None),
        height=dp(56),
        elevation=2
    )

    button_scroll = ScrollView(
        do_scroll_x=True,
        do_scroll_y=False,
        bar_width=0
    )

    button_container = MDBoxLayout(
        orientation="horizontal",
        size_hint=(None, None),
        height=dp(45),
        spacing=dp(4)
    )
    button_container.bind(minimum_width=button_container.setter('width'))

    plot_btn = MDButton(
        MDButtonText(text="График", font_size="18sp"),
        style="filled",
        size_hint=(None, None),
        width=dp(90),
        height=dp(45),
        on_release=app_instance.plot_function
    )

    reset_btn = MDButton(
        MDButtonText(text="Сброс", font_size="18sp"),
        style="filled",
        size_hint=(None, None),
        width=dp(90),
        height=dp(45),
        on_release=app_instance.reset_function,
        md_bg_color=(0.3, 0.6, 0.3, 1)
    )

    analyze_btn = MDButton(
        MDButtonText(text="Анализ", font_size="18sp"),
        style="filled",
        size_hint=(None, None),
        width=dp(90),
        height=dp(45),
        on_release=app_instance.analyze_function,
        md_bg_color=(0.2, 0.6, 0.8, 1)
    )

    screenshot_btn = MDButton(
        MDButtonText(text="Фото", font_size="18sp"),
        style="filled",
        size_hint=(None, None),
        width=dp(90),
        height=dp(45),
        on_release=app_instance.save_screenshot,
        md_bg_color=(0.5, 0.5, 0.5, 1)
    )

    button_container.add_widget(plot_btn)
    button_container.add_widget(reset_btn)
    button_container.add_widget(analyze_btn)
    button_container.add_widget(screenshot_btn)

    button_scroll.add_widget(button_container)
    button_card.add_widget(button_scroll)
    content.add_widget(button_card)

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

    # === Управление диапазонами (видимая область) ===
    control_card = MDCard(
        orientation="vertical",
        padding=dp(15),
        size_hint=(1, None),
        height=dp(120),
        elevation=2
    )
    control_title = MDLabel(
        text="Диапазоны отображения:",
        role="medium",
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
        role="medium",
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