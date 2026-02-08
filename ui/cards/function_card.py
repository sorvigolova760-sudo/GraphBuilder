"""
Модуль для карточки ввода функций
"""
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp


def create_function_card(app_instance, title_text, default_text, hint_text):
    """
    Создает карточку для ввода одной функции.
    """
    card = MDCard(
        orientation="vertical",
        padding=dp(12),
        size_hint=(1, None),
        height=dp(90),
        elevation=2
    )
    title = MDLabel(
        text=title_text,
        role="small",
        size_hint=(1, None),
        height=dp(20)
    )
    card.add_widget(title)
    text_field = MDTextField(
        text=default_text,
        hint_text=hint_text,
        mode="filled",
        font_size='14sp'
    )
    card.add_widget(text_field)
    return card, text_field