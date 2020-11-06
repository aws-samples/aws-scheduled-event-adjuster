import boto3


class AutoScalingService:
    def __init__(self, client=None):
        if not client:
            self._client = boto3.client('autoscaling')
        else:
            self._client = client

    def get_client(self):
        return self._client

    def get_asgs(self):
        paginator = self._client.get_paginator('describe_auto_scaling_groups')
        result = []
        for asg in paginator.paginate():
            result = result + asg['AutoScalingGroups']
        return result

    def get_asg_scheduled_actions(self, asg_name):
        paginator = self._client.get_paginator('describe_scheduled_actions')
        result = []
        for action in paginator.paginate(AutoScalingGroupName=asg_name):
            result = result + action['ScheduledUpdateGroupActions']
        return result

    def update_asg_scheduled_actions(self, asg_name, action_updates):
        return self._client.batch_put_scheduled_update_group_action(
            AutoScalingGroupName=asg_name,
            ScheduledUpdateGroupActions=action_updates
        )


class EventBridgeService:
    def __init__(self, client=None):
        if not client:
            self._client = boto3.client('events')
        else:
            self._client = client

    def get_client(self):
        return self._client

    def get_scheduled_rules(self):
        """Returns all EventBridge scheduled rules in the active AWS account.
        """
        paginator = self._client.get_paginator('list_rules')
        result = []
        # Scheduled rules can only exist in the default bus (see
        # https://docs.aws.amazon.com/eventbridge/latest/userguide/create-eventbridge-scheduled-rule.html).
        for page in paginator.paginate(EventBusName='default'):
            result = result + [rule for rule in page['Rules'] if 'ScheduleExpression' in rule]
        return result
