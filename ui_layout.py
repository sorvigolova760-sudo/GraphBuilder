# ui_layout.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from graph_widget import GraphWidget

def build_ui(app_instance):
    main_layout = MDBoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

    # === Верхняя панель ===
    top_panel = MDBoxLayout(orientation="vertical", size_hint=(1, None), height=dp(150), spacing=dp(10))
    title = MDLabel(
        text="📈 Построитель графиков функций",
        halign="center", font_style="H5", size_hint=(1, None), height=dp(40)
    )
    top_panel.add_widget(title)
    input_card = MDCard(orientation="vertical", padding=dp(15), size_hint=(1, None), height=dp(100), elevation=2)
    input_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10))
    app_instance.func_input = MDTextField(
        text="x**2",
        hint_text="Введите функцию, например: x**2 или sin(x)",
        mode="rectangle",
        size_hint=(0.7, None),
        height=dp(50),
        font_size='16sp'
    )
    plot_btn = MDRaisedButton(
        text="Построить",
        size_hint=(0.3, None),
        height=dp(50),
        on_press=app_instance.plot_function
    )
    input_layout.add_widget(app_instance.func_input)
    input_layout.add_widget(plot_btn)
    input_card.add_widget(input_layout)
    top_panel.add_widget(input_card)
    main_layout.add_widget(top_panel)

    # === График ===
    graph_card = MDCard(
        padding=dp(10),
        size_hint=(1, 0.6),
        elevation=3,
        radius=[15, 15, 15, 15],
        md_bg_color=(0.95, 0.95, 0.95, 1)
    )
    app_instance.graph = GraphWidget()
    graph_card.add_widget(app_instance.graph)
    main_layout.add_widget(graph_card)

    # === Управление и примеры ===
    bottom_panel = MDBoxLayout(orientation="vertical", size_hint=(1, None), height=dp(250), spacing=dp(10))
    
    control_card = MDCard(orientation="vertical", padding=dp(15), size_hint=(1, None), height=dp(120), elevation=2)
    control_title = MDLabel(text="Диапазоны отображения:", font_style="Subtitle1", size_hint=(1, None), height=dp(30))
    control_card.add_widget(control_title)
    range_grid = MDGridLayout(cols=4, spacing=dp(10), size_hint=(1, None), height=dp(50))
    app_instance.x_min_input = MDTextField(text="-5", hint_text="X min", mode="rectangle", input_filter="float")
    app_instance.x_max_input = MDTextField(text="5", hint_text="X max", mode="rectangle", input_filter="float")
    app_instance.y_min_input = MDTextField(text="-5", hint_text="Y min", mode="rectangle", input_filter="float")
    app_instance.y_max_input = MDTextField(text="5", hint_text="Y max", mode="rectangle", input_filter="float")
    range_grid.add_widget(app_instance.x_min_input)
    range_grid.add_widget(app_instance.x_max_input)
    range_grid.add_widget(app_instance.y_min_input)
    range_grid.add_widget(app_instance.y_max_input)
    control_card.add_widget(range_grid)
    bottom_panel.add_widget(control_card)

    examples_card = MDCard(orientation="vertical", padding=dp(15), size_hint=(1, None), height=dp(120), elevation=2)
    examples_title = MDLabel(text="Примеры функций:", font_style="Subtitle1", size_hint=(1, None), height=dp(30))
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
    bottom_panel.add_widget(examples_card)

    main_layout.add_widget(bottom_panel)
    return main_layout