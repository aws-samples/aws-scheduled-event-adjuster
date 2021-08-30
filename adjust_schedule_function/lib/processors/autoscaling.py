# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from lib import utils
from lib.processors.base import ResourceProcessor

class AutoScalingGroupProcessor(ResourceProcessor):
    def __init__(self, tag_prefix, asg_service, recurrence_calculator):
        super().__init__(tag_prefix)
        self._asg_service = asg_service
        self._recurrence_calculator = recurrence_calculator

    def process_resources(self):
        changes = []

        asgs = self._asg_service.get_asgs()
        for asg in asgs:
            changes = changes + self._process_asg(asg)

        return changes

    def _process_asg(self, asg):
        result = []
        asg_name = asg['AutoScalingGroupName']

        print("Processing ASG '{}'".format(asg_name))

        if utils.get_tag_by_key(asg['Tags'], self._get_enabled_tag()) == None:
            print("Skipping: ASG '{}' is not enabled (missing tag '{}')".format(asg_name,
                                                                                self._get_enabled_tag()))
            return result

        local_timezone = utils.get_tag_by_key(asg['Tags'], self._get_local_timezone_tag())
        if not local_timezone:
            print("Skipping: ASG '{}' has no timezone defined (missing tag '{}')".format(asg_name,
                                                                                         self._get_local_timezone_tag()))
            return result

        scheduled_actions = self._asg_service.get_asg_scheduled_actions(asg_name)
        scheduled_action_updates = []

        for action in scheduled_actions:
            action_name = action['ScheduledActionName']
            current_recurrence = action['Recurrence']

            local_time_tag_key = self._get_local_time_tag() + ':' + action_name
            local_time = utils.get_tag_by_key(asg['Tags'], local_time_tag_key)
            if not local_time:
                print("Skipping: action '{}' does not have local time tag (missing tag '{}')".format(action_name, local_time_tag_key))
                continue

            print("Processing action '{}'".format(action_name))

            correct_recurrence = self._recurrence_calculator.calculate_recurrence(current_recurrence,
                                                                                  local_time,
                                                                                  local_timezone)
            if correct_recurrence != current_recurrence:
                print("Calculated recurrence '{}' does not match current recurrence '{}'. This action will be updated.".format(correct_recurrence, current_recurrence))
                scheduled_action_updates.append({
                    'ScheduledActionName': action_name,
                    'Recurrence': correct_recurrence,
                    # Need to specify one of min, max or desired
                    'DesiredCapacity': action['DesiredCapacity']
                })

                result.append({
                    'Type': 'AutoScalingGroupScalingPolicy',
                    'ResourceName': asg_name,
                    'ResourceArn': asg['AutoScalingGroupARN'],
                    'OriginalRecurrence': current_recurrence,
                    'NewRecurrence': correct_recurrence,
                    'LocalTime': local_time,
                    'LocalTimezone': local_timezone,
                    'AdditionalDetails': {'ActionName': action_name}
                })

        if not len(scheduled_action_updates):
            print("No scheduled actions need to be updated for ASG '{}'".format(asg_name))
        else:
            print("There are actions which need to be updated. Updating them now.")
            update_response = self._asg_service.update_asg_scheduled_actions(asg_name,
                                                                            scheduled_action_updates)

            if len(update_response['FailedScheduledUpdateGroupActions']):
                print(update_response['FailedScheduledUpdateGroupActions'])
                raise Exception('{} actions failed to update'.format(len(update_response['FailedScheduledUpdateGroupActions'])))

        return result
