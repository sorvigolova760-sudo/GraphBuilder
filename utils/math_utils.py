"""
Утилиты для математических операций
"""
import math


def nice_number(value):
    """
    Возвращает "красивое" округленное число.
    """
    if value <= 0:
        return 1.0
    exponent = math.floor(math.log10(value))
    fraction = value / (10 ** exponent)
    nice_fractions = [1, 2, 5, 10]
    nice_fraction = min(nice_fractions, key=lambda x: abs(x - fraction))
    return nice_fraction * (10 ** exponent)