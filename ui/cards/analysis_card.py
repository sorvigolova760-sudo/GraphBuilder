"""
Модуль для карточки отображения анализа функции
"""
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.metrics import dp


def create_analysis_card(analysis_text):
    """
    Создает карточку с результатами анализа функции.
    """
    card = MDCard(
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
    card.add_widget(label)
    return card