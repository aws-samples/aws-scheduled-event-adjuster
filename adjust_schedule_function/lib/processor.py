from lib import utils

class AutoScalingGroupProcessor:
    # The tag that determines whether the ASG should be processed by this script.
    ENABLED_TAG = 'scheduled-event-adjuster:enabled'

    # The tag that determines the timezone of the local time.
    LOCAL_TIMEZONE_TAG = 'scheduled-event-adjuster:local-timezone'

    # The prefix of the tag that determines the local time at which the scaling
    # policy is expected to run.
    LOCAL_TIME_TAG_PREFIX = 'scheduled-event-adjuster:local-time:'

    def __init__(self, asg_service, recurrence_calculator):
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

        if utils.get_tag_by_key(asg['Tags'], self.ENABLED_TAG) == None:
            print("Skipping: ASG '{}' is not enabled (missing tag '{}')".format(asg_name,
                                                                                self.ENABLED_TAG))
            return result

        local_timezone = utils.get_tag_by_key(asg['Tags'], self.LOCAL_TIMEZONE_TAG)
        if not local_timezone:
            print("Skipping: ASG '{}' has no timezone defined (missing tag '{}')".format(asg_name,
                                                                                         self.LOCAL_TIMEZONE_TAG))
            return result

        scheduled_actions = self._asg_service.get_asg_scheduled_actions(asg_name)
        scheduled_action_updates = []

        for action in scheduled_actions:
            action_name = action['ScheduledActionName']
            current_recurrence = action['Recurrence']

            local_time = utils.get_tag_by_key(asg['Tags'],
                                              self.LOCAL_TIME_TAG_PREFIX + action_name)
            if not local_time:
                print("Skipping: action '{}' does not have local time tag (missing tag '{}')".format(action_name,
                                                                                                     self.LOCAL_TIME_TAG_PREFIX + action_name))
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
