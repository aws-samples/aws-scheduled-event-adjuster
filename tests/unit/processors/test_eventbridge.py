from lib.processors.eventbridge import EventBridgeProcessor
from lib.recurrence import RecurrenceCalculator
from lib.services import EventBridgeService
import pytest


def test_process_resources_updates_schedule_when_recurrences_are_different(mocker):
    rules = [{'Name': 'ruleName', 'Arn': 'ruleArn', 'ScheduleExpression': 'cron(foo)'}]
    tags = [
        {'Key': 'scheduled-event-adjuster:enabled', 'Value': ''},
        {'Key': 'scheduled-event-adjuster:local-timezone', 'Value': 'Europe/Madrid'},
        {'Key': 'scheduled-event-adjuster:local-time', 'Value': '10:00'}
    ]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)
    mocker.patch.object(eb_svc, 'update_rule_schedule', return_value=None)
    mocker.patch.object(rec_calc, 'calculate_recurrence', return_value='bar')

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    rec_calc.calculate_recurrence.assert_called_once_with('foo', '10:00', 'Europe/Madrid')
    eb_svc.update_rule_schedule.assert_called_once_with('ruleName', 'cron(bar)')
    assert len(changes) == 1
    assert changes[0] == {
        'Type': 'EventBridgeRule',
        'ResourceName': 'ruleName',
        'ResourceArn': 'ruleArn',
        'OriginalRecurrence': 'foo',
        'NewRecurrence': 'bar',
        'LocalTime': '10:00',
        'LocalTimezone': 'Europe/Madrid'
    }

def test_process_resources_skips_update_when_an_exception_is_thrown_when_updating_schedule(mocker):
    rules = [{'Name': 'ruleName', 'Arn': 'ruleArn', 'ScheduleExpression': 'cron(foo)'}]
    tags = [
        {'Key': 'scheduled-event-adjuster:enabled', 'Value': ''},
        {'Key': 'scheduled-event-adjuster:local-timezone', 'Value': 'Europe/Madrid'},
        {'Key': 'scheduled-event-adjuster:local-time', 'Value': '10:00'}
    ]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)
    mocker.patch.object(eb_svc, 'update_rule_schedule', side_effect=Exception('mocked exception'))
    mocker.patch.object(rec_calc, 'calculate_recurrence', return_value='bar')

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    eb_svc.update_rule_schedule.assert_called_once_with('ruleName', 'cron(bar)')
    assert len(changes) == 0

def test_process_resources_with_same_recurrence(mocker):
    rules = [{'Arn': 'ruleArn', 'ScheduleExpression': 'cron(foo)'}]
    tags = [
        {'Key': 'scheduled-event-adjuster:enabled', 'Value': ''},
        {'Key': 'scheduled-event-adjuster:local-timezone', 'Value': 'Europe/Madrid'}
    ]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)
    mocker.patch.object(rec_calc, 'calculate_recurrence', return_value='foo')

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    assert len(changes) == 0

def test_process_resources_without_enabled_tag(mocker):
    rules = [{'Arn': 'ruleArn'}]
    tags = [{'Key': 'nope', 'Value': 'nope'}]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    assert len(changes) == 0

def test_process_resources_without_timezone_tag(mocker):
    rules = [{'Arn': 'ruleArn'}]
    tags = [{'Key': 'scheduled-event-adjuster:enabled', 'Value': ''}]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    assert len(changes) == 0

def test_process_resources_without_local_time_tag(mocker):
    rules = [{'Arn': 'ruleArn'}]
    tags = [
        {'Key': 'scheduled-event-adjuster:enabled', 'Value': ''},
        {'Key': 'scheduled-event-adjuster:local-timezone', 'Value': 'Europe/Madrid'},
    ]
    eb_svc = EventBridgeService()
    rec_calc = RecurrenceCalculator()
    processor = EventBridgeProcessor(eb_svc, rec_calc)
    mocker.patch.object(eb_svc, 'get_scheduled_rules', return_value=rules)
    mocker.patch.object(eb_svc, 'get_rule_tags', return_value=tags)

    changes = processor.process_resources()

    eb_svc.get_rule_tags.assert_called_once_with('ruleArn')
    assert len(changes) == 0
