from lib.processors.autoscaling import AutoScalingGroupProcessor
from lib.recurrence import RecurrenceCalculator
from lib.services import AutoScalingService
import pytest


def test_process_resources_with_different_recurrence(mocker):
    asgs = [
        {
            'AutoScalingGroupName': 'MyAsg',
            'AutoScalingGroupARN': 'MyAsgARN',
            'Tags': [
                {
                    'Key': 'scheduled-event-adjuster:enabled',
                    'Value': ''
                },
                {
                    'Key': 'scheduled-event-adjuster:local-timezone',
                    'Value': 'Europe/Madrid'
                },
                {
                    'Key': 'scheduled-event-adjuster:local-time:ActionOne',
                    'Value': '10:00'
                }
            ]
        }
    ]
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_svc = AutoScalingService()
    rec_calc = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_svc, rec_calc)
    mocker.patch.object(asg_svc, 'get_asgs', return_value=asgs)
    mocker.patch.object(asg_svc, 'get_asg_scheduled_actions', return_value=scheduled_actions)
    mocker.patch.object(asg_svc, 'update_asg_scheduled_actions')
    mocker.patch.object(rec_calc, 'calculate_recurrence', return_value='NewRecurrence')

    result = processor.process_resources()

    rec_calc.calculate_recurrence.assert_called_once_with('OriginalRecurrence',
                                                          '10:00',
                                                          'Europe/Madrid')
    asg_svc.update_asg_scheduled_actions.assert_called_once_with(
        'MyAsg',
        [
            {
                'ScheduledActionName': 'ActionOne',
                'Recurrence': 'NewRecurrence',
                'DesiredCapacity': 123
            }
        ]
    )
    assert len(result) == 1
    assert result[0] == {
        'Type': 'AutoScalingGroupScalingPolicy',
        'ResourceName': 'MyAsg',
        'ResourceArn': 'MyAsgARN',
        'OriginalRecurrence': 'OriginalRecurrence',
        'NewRecurrence': 'NewRecurrence',
        'LocalTime': '10:00',
        'LocalTimezone': 'Europe/Madrid',
        'AdditionalDetails': {
            'ActionName': 'ActionOne'
        }
    }

def test_process_resources_with_same_recurrence(mocker):
    asgs = [
        {
            'AutoScalingGroupName': 'MyAsg',
            'AutoScalingGroupARN': 'MyAsgARN',
            'Tags': [
                {
                    'Key': 'scheduled-event-adjuster:enabled',
                    'Value': ''
                },
                {
                    'Key': 'scheduled-event-adjuster:local-timezone',
                    'Value': 'Europe/Madrid'
                },
                {
                    'Key': 'scheduled-event-adjuster:local-time:ActionOne',
                    'Value': '10:00'
                }
            ]
        }
    ]
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_svc = AutoScalingService()
    rec_calc = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_svc, rec_calc)
    mocker.patch.object(asg_svc, 'get_asgs', return_value=asgs)
    mocker.patch.object(asg_svc, 'get_asg_scheduled_actions', return_value=scheduled_actions)
    mocker.patch.object(asg_svc, 'update_asg_scheduled_actions')
    mocker.patch.object(rec_calc, 'calculate_recurrence', return_value='OriginalRecurrence')

    result = processor.process_resources()

    asg_svc.update_asg_scheduled_actions.assert_not_called()
    assert len(result) == 0

def test_process_resources_without_enabled_tag(mocker):
    asgs = [
        {
            'AutoScalingGroupName': 'MyAsg',
            'AutoScalingGroupARN': 'MyAsgARN',
            'Tags': []
        }
    ]
    asg_svc = AutoScalingService()
    rec_calc = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_svc, rec_calc)
    mocker.patch.object(asg_svc, 'get_asgs', return_value=asgs)

    result = processor.process_resources()

    assert len(result) == 0

def test_process_resources_without_timezone_tag(mocker):
    asgs = [
        {
            'AutoScalingGroupName': 'MyAsg',
            'AutoScalingGroupARN': 'MyAsgARN',
            'Tags': [{'Key': 'scheduled-event-adjuster:enabled', 'Value': ''}]
        }
    ]
    asg_svc = AutoScalingService()
    rec_calc = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_svc, rec_calc)
    mocker.patch.object(asg_svc, 'get_asgs', return_value=asgs)

    result = processor.process_resources()

    assert len(result) == 0

def test_process_asg_without_action_time_tag(mocker):
    asgs = [
        {
            'AutoScalingGroupName': 'MyAsg',
            'AutoScalingGroupARN': 'MyAsgARN',
            'Tags': [
                {'Key': 'scheduled-event-adjuster:enabled', 'Value': ''},
                {'Key': 'scheduled-event-adjuster:local-timezone', 'Value': 'Europe/Madrid'}
            ]
        }
    ]
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_svc = AutoScalingService()
    rec_calc = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_svc, rec_calc)
    mocker.patch.object(asg_svc, 'get_asgs', return_value=asgs)
    mocker.patch.object(asg_svc, 'get_asg_scheduled_actions', return_value=scheduled_actions)

    result = processor.process_resources()

    assert len(result) == 0
