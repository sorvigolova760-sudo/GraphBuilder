"""
Модуль для карточки управления параметрами функции
"""
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider
from kivy.metrics import dp


def create_parameter_card(app_instance, params):
    """
    Создает карточку с слайдерами для параметров функции.
    """
    card = MDCard(
        orientation="vertical",
        padding=dp(15),
        size_hint=(1, None),
        height=dp(40 + len(params) * 60),
        elevation=2,
        radius=[10]
    )

    title = MDLabel(text="Параметры функции:", role="medium", size_hint=(1, None), height=dp(30))
    card.add_widget(title)

    for p in params:
        current_value = 1.0
        if hasattr(app_instance, f"{p}_slider"):
            current_value = getattr(app_instance, f"{p}_slider").value

        label = MDLabel(
            text=f"{p} = {current_value:.2f}",
            halign="left",
            size_hint=(1, None),
            height=dp(20)
        )
        setattr(app_instance, f"{p}_label", label)

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
                _on_slider_change(app_instance, param, lbl, value)
        )
        setattr(app_instance, f"{p}_slider", slider)

        card.add_widget(label)
        card.add_widget(slider)

    return card


def _on_slider_change(app_instance, param_name, label, value):
    """
    Обработчик изменения слайдера параметра.
    """
    rounded_value = round(value * 2) / 2
    label.text = f"{param_name} = {rounded_value:.1f}"
    # Перестраиваем график с новыми значениями параметров
    app_instance._rebuild_graph_with_current_params()