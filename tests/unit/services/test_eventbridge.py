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

def test_get_rule_tags():
    eventbridge_boto3_client = boto3.client('events')
    stubber = Stubber(eventbridge_boto3_client)
    stubber.add_response('list_tags_for_resource',
                        {'Tags': [{'Key': 'foo', 'Value': 'bar'}]},
                        {'ResourceARN': 'theArn'})
    stubber.activate()
    service = EventBridgeService(eventbridge_boto3_client)

    tags = service.get_rule_tags('theArn')

    assert tags == [{'Key': 'foo', 'Value': 'bar'}]

def test_update_rule_schedule():
    eventbridge_boto3_client = boto3.client('events')
    stubber = Stubber(eventbridge_boto3_client)
    stubber.add_response('put_rule',
                        {'RuleArn': 'theArn'},
                        {'Name': 'theName', 'ScheduleExpression': 'foo'})
    stubber.activate()
    service = EventBridgeService(eventbridge_boto3_client)

    tags = service.update_rule_schedule('theName', 'foo')
