import boto3
from lib.autoscaling import AutoScalingClient
from lib.events import EventBus
from lib.recurrence import RecurrenceCalculator
from lib import utils
import logging
import os

# The tag that determines whether the ASG should be processed by this script.
ENABLED_TAG = 'scheduled-scaling-adjuster:enabled'

# The prefix of the tag that determines the local time at which the scaling
# policy is expected to run.
LOCAL_TIME_TAG_PREFIX = 'scheduled-scaling-adjuster:local-time:'

# The tag that determines the timezone of the local time.
LOCAL_TIMEZONE_TAG = 'scheduled-scaling-adjuster:local-timezone'

asg_client = AutoScalingClient(boto3.client('autoscaling'))
bus = EventBus(boto3.client('events'))
recurrence_calculator = RecurrenceCalculator()


def process_asg(asg, local_timezone):
    asg_name = asg['AutoScalingGroupName']
    scheduled_actions = asg_client.get_asg_scheduled_actions(asg_name=asg_name)
    scheduled_action_updates = []

    for action in scheduled_actions['ScheduledUpdateGroupActions']:
        action_name = action['ScheduledActionName']
        current_recurrence = action['Recurrence']

        local_time = utils.get_tag_by_key(asg['Tags'], LOCAL_TIME_TAG_PREFIX + action_name)
        if not local_time:
            print("Skipping: action '{}' does not have local time tag (missing tag '{}')".format(action_name, LOCAL_TIME_TAG_PREFIX + action_name))
            continue

        print("Processing action '{}'".format(action_name))

        correct_recurrence = recurrence_calculator.calculate_recurrence(action, local_time, local_timezone)
        if correct_recurrence != current_recurrence:
            print("Calculated recurrence '{}' does not match current recurrence '{}'. This action will be updated.".format(correct_recurrence, current_recurrence))
            scheduled_action_updates.append({
                'ScheduledActionName': action_name,
                'Recurrence': correct_recurrence,
                # Need to specify one of min, max or desired
                'DesiredCapacity': action['DesiredCapacity']
            })

    if not len(scheduled_action_updates):
        print("No scheduled actions need to be updated for ASG '{}'".format(asg_name))
    else:
        print("There are actions which need to be updated. Updating them now.")
        update_response = asg_client.update_asg_scheduled_actions(asg_name,
                                                                  scheduled_action_updates)

        if len(update_response['FailedScheduledUpdateGroupActions']):
            print(update_response['FailedScheduledUpdateGroupActions'])
            raise Exception('{} actions failed to update'.format(len(update_response['FailedScheduledUpdateGroupActions'])))


def lambda_handler(event, context):
    for asg in asg_client.get_asgs()['AutoScalingGroups']:
        asg_name = asg['AutoScalingGroupName']

        if not utils.get_tag_by_key(asg['Tags'], ENABLED_TAG):
            print("Skipping: ASG '{}' is not enabled (missing tag '{}')".format(asg_name, ENABLED_TAG))
            continue

        local_timezone = utils.get_tag_by_key(asg['Tags'], LOCAL_TIMEZONE_TAG)
        if not local_timezone:
            print("Skipping: ASG '{}' has no timezone defined (missing tag '{}')".format(asg_name, LOCAL_TIMEZONE_TAG))
            continue

        try:
            print("Processing ASG '{}'".format(asg_name))
            process_asg(asg, local_timezone)
            print("ASG '{}' has been processed successfully".format(asg_name))
        except:
            print("ASG '{}' failed to be processed".format(asg_name))
            raise

    print(bus.emit_process_completed({'dummy': 'payload'}))
    print("All ASGs have been processed. No further work to do.")
