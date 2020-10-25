import boto3
from lib.autoscaling import AutoScalingClient
from lib.events import EventBus
from lib.processor import AutoScalingGroupProcessor
from lib.recurrence import RecurrenceCalculator
from lib import utils
import logging
import os


asg_client = AutoScalingClient(boto3.client('autoscaling'))
asg_processor = AutoScalingGroupProcessor(asg_client, RecurrenceCalculator())
bus = EventBus(boto3.client('events'))


def lambda_handler(event, context):
    for asg in asg_client.get_asgs():
        asg_name = asg['AutoScalingGroupName']

        try:
            print("Processing ASG '{}'".format(asg_name))
            results = asg_processor.process_asg(asg)
            print("ASG '{}' has been processed successfully".format(asg_name))
        except:
            print("ASG '{}' failed to be processed".format(asg_name))
            raise

    if len(results):
        print('Emitting event to bus')
        bus.emit_process_completed({'Updates': results})

    print("All ASGs have been processed. No further work to do.")
