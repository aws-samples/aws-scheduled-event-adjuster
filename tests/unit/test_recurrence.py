from datetime import datetime
import pytest
from lib.recurrence import parse_cron_expression, RecurrenceCalculator, TimeSource

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
    parsed = parse_cron_expression(expression)

    assert parsed == expected


@pytest.mark.parametrize('expression', get_invalid_expressions())
def test_parse_cron_expression_with_invalid_expression(expression):
    with pytest.raises(Exception):
        parse_cron_expression(expression)


def get_calculate_recurrence_inputs():
    return [
        # Recurrence is wrong
        ('Europe/Madrid', '11:00', datetime(2019, 1, 1), datetime(2020, 1, 1), '30 0 * * *', '0 10 * * *'),
        ('Europe/Madrid', '23:30', datetime(2019, 1, 1), datetime(2020, 1, 1), '15 8 * * *', '30 22 * * *'),
        # Recurrence is already correct
        ('Europe/Madrid', '11:00', datetime(2019, 1, 1), datetime(2020, 1, 1), '0 10 * * *', '0 10 * * *'),
        ('Europe/Madrid', '23:30', datetime(2019, 1, 1), datetime(2020, 1, 1), '30 22 * * *', '30 22 * * *'),
        # Action start date is over a day into the future
        ('Europe/Madrid', '11:00', datetime(2020, 1, 3), datetime(2020, 1, 1), '0 15 * * *', '0 15 * * *'),
    ]


@pytest.mark.parametrize('tz,lt,start,now,current_recurrence,expected_recurrence', get_calculate_recurrence_inputs())
def test_calculate_recurrence(tz,
                              lt,
                              start,
                              now,
                              current_recurrence,
                              expected_recurrence,
                              mocker):
    action = {
        'AutoScalingGroupName': 'asg',
        'ScheduledActionName': 'action',
        'StartTime': start,
        'Recurrence': current_recurrence
    }
    time_source = TimeSource()
    calculator = RecurrenceCalculator(time_source)
    mocker.patch('lib.recurrence.TimeSource.get_current_utc_datetime',
                 lambda self: now)

    calculated_recurrence = calculator.calculate_recurrence(action, lt, tz)

    assert calculated_recurrence == expected_recurrence


@pytest.mark.parametrize('recurrence', [
    '0 6-9 * * *',
    '0 6,7 * * *',
    '0-3 0 * * *',
    '0,1 0 * * *'
])
def test_calculate_recurrence_with_unsupported_recurrences(recurrence):
    action = {
        'AutoScalingGroupName': 'asg',
        'ScheduledActionName': 'action',
        'StartTime': datetime(2020, 1, 1),
        'Recurrence': recurrence
    }
    calculator = RecurrenceCalculator()


    with pytest.raises(NotImplementedError):
        calculated_recurrence = calculator.calculate_recurrence(action, '00:00', 'Europe/Madrid')
