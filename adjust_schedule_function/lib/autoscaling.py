import boto3


class AutoScalingClient:
    def __init__(self, client=None):
        if not client:
            self._client = boto3.client('autoscaling')
        else:
            self._client = client

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
