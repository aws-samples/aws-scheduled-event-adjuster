class AutoScalingClient(object):

    def __init__(self, client):
        self._client = client

    def get_asgs(self):
    	# To-Do: use paginators instead
        return self._client.describe_auto_scaling_groups()

    def get_asg_scheduled_actions(self, asg_name):
        return self._client.describe_scheduled_actions(
        	AutoScalingGroupName=asg_name
        )

    def update_asg_scheduled_actions(self, asg_name, action_updates):
    	return self._client.batch_put_scheduled_update_group_action(
            AutoScalingGroupName=asg_name,
            ScheduledUpdateGroupActions=action_updates
        )
