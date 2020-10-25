import pytest
from lib import recurrence


def get_valid_expressions():
    return [
        ('30 15 * * * *', {'minute': '30', 'hour': '15', 'rest': '* * * *'}),
        ('30 15 * * *', {'minute': '30', 'hour': '15', 'rest': '* * *'})
    ]


def get_invalid_expressions():
    return [
        '30 15 * *',
        '30 15 * * * * *',
        'foo',
        None,
        False
    ]


@pytest.mark.parametrize('expression,expected', get_valid_expressions())
def test_parse_cron_expression(expression, expected):
    parsed = recurrence.parse_cron_expression(expression)

    assert parsed == expected


@pytest.mark.parametrize('expression', get_invalid_expressions())
def test_parse_cron_expression_with_invalid_expression(expression):
    with pytest.raises(Exception):
        recurrence.parse_cron_expression(expression)
