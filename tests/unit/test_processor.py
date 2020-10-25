from lib.autoscaling import AutoScalingClient
from lib.processor import AutoScalingGroupProcessor
from lib.recurrence import RecurrenceCalculator
import pytest


def test_process_asg_with_different_recurrence(mocker):
    asg = {
        'AutoScalingGroupName': 'MyAsg',
        'AutoScalingGroupARN': 'MyAsgARN',
        'Tags': [
            {
                'Key': 'scheduled-scaling-adjuster:enabled',
                'Value': ''
            },
            {
                'Key': 'scheduled-scaling-adjuster:local-timezone',
                'Value': 'Europe/Madrid'
            },
            {
                'Key': 'scheduled-scaling-adjuster:local-time:ActionOne',
                'Value': '10:00'
            }
        ]
    }
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_client = AutoScalingClient()
    recurrence_calculator = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_client, recurrence_calculator)
    mocker.patch('lib.autoscaling.AutoScalingClient.get_asg_scheduled_actions',
                 lambda self, x: scheduled_actions)
    mocker.patch('lib.autoscaling.AutoScalingClient.update_asg_scheduled_actions')
    mocker.patch('lib.recurrence.RecurrenceCalculator.calculate_recurrence',
                 lambda self, action, time, tz: 'NewRecurrence')

    result = processor.process_asg(asg)

    asg_client.update_asg_scheduled_actions.assert_called_once_with(
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
        'ActionName': 'ActionOne',
        'AsgName': 'MyAsg',
        'LocalTime': '10:00',
        'OriginalRecurrence': 'OriginalRecurrence',
        'NewRecurrence': 'NewRecurrence'
    }

def test_process_asg_with_same_recurrence(mocker):
    asg = {
        'AutoScalingGroupName': 'MyAsg',
        'AutoScalingGroupARN': 'MyAsgARN',
        'Tags': [
            {
                'Key': 'scheduled-scaling-adjuster:enabled',
                'Value': ''
            },
            {
                'Key': 'scheduled-scaling-adjuster:local-timezone',
                'Value': 'Europe/Madrid'
            },
            {
                'Key': 'scheduled-scaling-adjuster:local-time:ActionOne',
                'Value': '10:00'
            }
        ]
    }
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_client = AutoScalingClient()
    recurrence_calculator = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_client, recurrence_calculator)
    mocker.patch('lib.autoscaling.AutoScalingClient.get_asg_scheduled_actions',
                 lambda self, x: scheduled_actions)
    mocker.patch('lib.autoscaling.AutoScalingClient.update_asg_scheduled_actions')
    mocker.patch('lib.recurrence.RecurrenceCalculator.calculate_recurrence',
                 lambda self, action, time, tz: 'OriginalRecurrence')

    result = processor.process_asg(asg)

    asg_client.update_asg_scheduled_actions.assert_not_called()
    assert len(result) == 0

def test_process_asg_without_enabled_tag():
    asg = {
        'AutoScalingGroupName': 'MyAsg',
        'AutoScalingGroupARN': 'MyAsgARN',
        'Tags': []
    }
    asg_client = AutoScalingClient()
    recurrence_calculator = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_client, recurrence_calculator)

    result = processor.process_asg(asg)

    assert len(result) == 0

def test_process_asg_without_timezone_tag():
    asg = {
        'AutoScalingGroupName': 'MyAsg',
        'AutoScalingGroupARN': 'MyAsgARN',
        'Tags': [{'Key': 'scheduled-scaling-adjuster:enabled', 'Value': ''}]
    }
    asg_client = AutoScalingClient()
    recurrence_calculator = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_client, recurrence_calculator)

    result = processor.process_asg(asg)

    assert len(result) == 0

def test_process_asg_without_action_time_tag(mocker):
    asg = {
        'AutoScalingGroupName': 'MyAsg',
        'AutoScalingGroupARN': 'MyAsgARN',
        'Tags': [
            {'Key': 'scheduled-scaling-adjuster:enabled', 'Value': ''},
            {'Key': 'scheduled-scaling-adjuster:local-timezone', 'Value': 'Europe/Madrid'}
        ]
    }
    scheduled_actions = [
        {
            'ScheduledActionName': 'ActionOne',
            'ScheduledActionARN': 'ActionOneARN',
            'Recurrence': 'OriginalRecurrence',
            'DesiredCapacity': 123
        }
    ]
    asg_client = AutoScalingClient()
    recurrence_calculator = RecurrenceCalculator()
    processor = AutoScalingGroupProcessor(asg_client, recurrence_calculator)
    mocker.patch('lib.autoscaling.AutoScalingClient.get_asg_scheduled_actions',
                 lambda self, x: scheduled_actions)

    result = processor.process_asg(asg)

    assert len(result) == 0
