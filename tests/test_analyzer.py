from parsers.function_parser import FunctionParser
from analyzers.standard_analyzer import StandardAnalyzer


def test_standard_analyzer_basic():
    f = FunctionParser.parse("x**2")
    analyzer = StandardAnalyzer(f, "x**2", -2, 2)
    a = analyzer.analyze()
    assert isinstance(a, dict)
    assert a.get('type') == 'standard'
    # Для x**2 на отрезке [-2,2] ожидаем ноль в 0
    assert 'x = 0' in a.get('zeros', '')
