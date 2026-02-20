import math
import numpy as np
from parsers.function_parser import FunctionParser
from parsers.parametric_parser import ParametricParser


def is_nan(x):
    try:
        return math.isnan(x)
    except Exception:
        return False


def test_parser_rejects_import_call():
    malicious = "__import__('os').system('echo hacked')"
    f = FunctionParser.parse(malicious)
    val = f(0)
    assert is_nan(val)


def test_parametric_rejects_import():
    x_func, y_func = ParametricParser.parse("__import__('os').system('ls')", "0")
    assert is_nan(x_func(0))
    assert abs(y_func(0) - 0.0) < 1e-8


def test_parser_rejects_attribute_access():
    malicious = "math.__dict__"
    f = FunctionParser.parse(malicious)
    val = f(0)
    assert is_nan(val)
