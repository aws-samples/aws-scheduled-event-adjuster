import boto3
from botocore.stub import Stubber
from datetime import datetime
from lib.autoscaling import AutoScalingClient
import pytest


def test_get_asgs():
    asg_boto3_client = boto3.client('autoscaling')
    stubber = Stubber(asg_boto3_client)
    asg = {
        'AutoScalingGroupName': 'foo',
        'MinSize': 0,
        'MaxSize': 0,
        'DesiredCapacity': 0,
        'DefaultCooldown': 0,
        'AvailabilityZones': ['foo'],
        'HealthCheckType': 'foo',
        'CreatedTime': datetime(2020, 1, 1)
    }
    response = {'AutoScalingGroups': [asg]}
    stubber.add_response('describe_auto_scaling_groups', response)
    stubber.activate()
    client = AutoScalingClient(asg_boto3_client)

    asgs = client.get_asgs()

    assert asgs == [asg]

def test_get_asg_scheduled_actions():
    asg_boto3_client = boto3.client('autoscaling')
    stubber = Stubber(asg_boto3_client)
    action = {
        'AutoScalingGroupName': 'foo',
        'ScheduledActionName': 'foo',
        'ScheduledActionARN': 'foo',
        'Time': datetime(2020, 1, 1),
        'StartTime': datetime(2020, 1, 1),
        'EndTime': datetime(2020, 1, 1),
        'Recurrence': 'foo',
        'MinSize': 123,
        'MaxSize': 123,
        'DesiredCapacity': 123
    }
    response = {'ScheduledUpdateGroupActions': [action]}
    stubber.add_response('describe_scheduled_actions',
                         response,
                         {'AutoScalingGroupName': 'foo'})
    stubber.activate()
    client = AutoScalingClient(asg_boto3_client)

    actions = client.get_asg_scheduled_actions('foo')

    assert actions == [action]
