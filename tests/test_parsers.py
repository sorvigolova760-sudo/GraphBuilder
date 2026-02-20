import math
from parsers.function_parser import FunctionParser
from parsers.parametric_parser import ParametricParser


def test_function_parser_polynomial():
    f = FunctionParser.parse("x**2")
    assert abs(f(2.0) - 4.0) < 1e-6


def test_function_parser_trig():
    f = FunctionParser.parse("sin(x)")
    assert abs(f(math.pi / 2) - 1.0) < 1e-6


def test_parametric_parser_circle():
    x_func, y_func = ParametricParser.parse("cos(t)", "sin(t)")
    assert abs(x_func(0.0) - 1.0) < 1e-6
    assert abs(y_func(math.pi / 2) - 1.0) < 1e-6
