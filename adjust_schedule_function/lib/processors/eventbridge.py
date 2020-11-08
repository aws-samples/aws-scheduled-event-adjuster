from lib import utils

class EventBridgeProcessor:
    # The tag that determines whether the resource should be processed by this script.
    ENABLED_TAG = 'scheduled-event-adjuster:enabled'

    # The tag that determines the timezone of the local time.
    LOCAL_TIMEZONE_TAG = 'scheduled-event-adjuster:local-timezone'

    # The tag that determines the local time at which the scheduled event is
    # expected to run.
    LOCAL_TIME_TAG = 'scheduled-event-adjuster:local-time'

    def __init__(self, eventbridge_service, recurrence_calculator):
        self._eventbridge_service = eventbridge_service
        self._recurrence_calculator = recurrence_calculator

    def process_resources(self):
        changes = []

        rules = self._eventbridge_service.get_scheduled_rules()

        for rule in rules:
            try:
                print("Processing EventBridge rule '{}'".format(rule['Name']))

                tags = self._eventbridge_service.get_rule_tags(rule['Arn'])

                if utils.get_tag_by_key(tags, self.ENABLED_TAG) == None:
                    print("Skipping: EventBridge rule '{}' is not enabled (missing tag '{}')".format(rule['Name'],
                                                                                                     self.ENABLED_TAG))
                    continue

                local_timezone = utils.get_tag_by_key(tags, self.LOCAL_TIMEZONE_TAG)
                local_time = utils.get_tag_by_key(tags, self.LOCAL_TIME_TAG)

                if not local_timezone:
                    print("Skipping: EventBridge rule '{}' has no timezone defined (missing tag '{}')".format(rule['Name'],
                                                                                                              self.LOCAL_TIMEZONE_TAG))
                    continue

                if not local_time:
                    print("Skipping: EventBridge rule '{}' does not have local time tag (missing tag '{}')".format(rule['Name'],
                                                                                                                   self.LOCAL_TIME_TAG))
                    continue

                # Remove the 'cron()' surrounding the cron expression itself,
                # as the calculator does not expect it.
                # (This should probably be transparent to the caller, and the
                # calculator should handle it instead.)
                current_recurrence = rule['ScheduleExpression'][5:][:-1]

                new_recurrence = self._recurrence_calculator.calculate_recurrence(current_recurrence,
                                                                                  local_time,
                                                                                  local_timezone)
                if new_recurrence != current_recurrence:
                    print("Calculated recurrence '{}' does not match current recurrence '{}'. This rule will be updated.".format(new_recurrence, current_recurrence))
                    self._eventbridge_service.update_rule_schedule(rule['Name'],
                                                                   'cron(' + new_recurrence + ')')
                    changes.append({
                        'Type': 'EventBridgeRule',
                        'ResourceName': rule['Name'],
                        'ResourceArn': rule['Arn'],
                        'OriginalRecurrence': current_recurrence,
                        'NewRecurrence': new_recurrence,
                        'LocalTime': local_time,
                        'LocalTimezone': local_timezone
                    })

            except Exception as e:
                print("EventBridge rule failed to be processed: {}".format(str(e)))

        return changes
