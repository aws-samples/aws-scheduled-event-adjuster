import boto3
from lib.events import EventBus
from lib.processors.autoscaling import AutoScalingGroupProcessor
from lib.processors.eventbridge import EventBridgeProcessor
from lib.recurrence import RecurrenceCalculator
from lib.services import AutoScalingService, EventBridgeService
from lib import utils
import logging
import os


tag_prefix = ''
if 'TAG_PREFIX' in os.environ and os.environ['TAG_PREFIX'].strip():
    tag_prefix = os.environ['TAG_PREFIX'].strip()

asg_service = AutoScalingService(boto3.client('autoscaling'))
eventbridge_service = EventBridgeService(boto3.client('events'))
processors = [
    AutoScalingGroupProcessor(tag_prefix, asg_service, RecurrenceCalculator()),
    EventBridgeProcessor(tag_prefix, eventbridge_service, RecurrenceCalculator()),
]
bus = EventBus(boto3.client('events'))


def lambda_handler(event, context):
    updates = []
    for processor in processors:
        print("Using processor '{}'".format(processor.__class__.__name__))
        updates = updates + processor.process_resources()
        print("Processor has completed")

    if len(updates):
        print('Emitting event to bus')
        bus.emit_process_completed(updates)

    print("All resources have been processed. No further work to do.")
