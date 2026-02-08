"""
Патч для корректной работы на Android
"""
import sys


def apply_android_patch():
    """
    Применяет патч для совместимости с Android.
    """
    if 'collections' in sys.modules:
        import collections.abc
        import collections
        collections.Mapping = collections.abc.Mapping
        collections.Sequence = collections.abc.Sequence
        sys.modules['collections'] = collections
        print("✅ Android collections patch applied")


# Применяем патч при импорте
apply_android_patch()
