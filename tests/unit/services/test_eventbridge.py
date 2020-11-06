import boto3
from botocore.stub import Stubber
from lib.services import EventBridgeService


def test_default_client_is_eventbridge_client():
    service = EventBridgeService()

    client = service.get_client()

    assert client.__module__ + '.' + client.__class__.__qualname__ == 'botocore.client.EventBridge'

def test_get_scheduled_rules():
    eventbridge_boto3_client = boto3.client('events')
    stubber = Stubber(eventbridge_boto3_client)
    pattern_based_rule = {
        'Name': 'EventBasedRule',
        'EventPattern': '{"foo":"bar"}'
    }
    scheduled_rule = {
        'Name': 'ScheduledRule',
        'ScheduleExpression': '* * * * * *'
    }
    response = {'Rules': [pattern_based_rule, scheduled_rule]}
    stubber.add_response('list_rules', response, {'EventBusName': 'default'})
    stubber.activate()
    service = EventBridgeService(eventbridge_boto3_client)

    rules = service.get_scheduled_rules()

    assert len(rules) == 1
    assert rules[0] == scheduled_rule
