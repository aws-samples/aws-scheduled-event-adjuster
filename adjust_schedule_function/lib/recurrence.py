from crontab import CronTab
from dateutil import parser
from datetime import datetime, timedelta
import pytz
import re


def parse_cron_expression(expression):
    pattern = r'^([^\s]+)\s+([^\s]+)((?:\s+[^\s]+){3,4})$'
    match = re.match(pattern, expression)

    if not match:
        raise Exception("String '{}' is not a valid cron expression".format(expression))

    return {
        'minute': match.group(1),
        'hour': match.group(2),
        'rest': match.group(3).strip()
    }


class TimeSource:
    """A time source that uses the standard datetime module."""
    def get_current_utc_datetime(self):
        return pytz.utc.localize(datetime.utcnow())


class RecurrenceCalculator:
    """A recurrence calculator for scheduled events.
    """
    def __init__(self, time_source=None):
        if not time_source:
            self._time_source = TimeSource()
        else:
            self._time_source = time_source

    def calculate_recurrence(self, current_recurrence, expected_time, timezone, start_time=None):
        """Calculates the correct recurrence expression for the given
        recurrence, expected local time and local timezone.

        The recurrence must be defined as a cron expression.

        If the recurrence is not selective on the hour, or if the start date
        will occur in more than a day in the future, this method will return
        the current recurrence.

        Args:
            current_recurrence: A string with the current recurrence, as a cron
                expression (e..g, '0 0 * * *')
            expected_time: A string with the local time at which the action is
                expected to run.
            timezone: The name of the timezone (e.g., 'Europe/Madrid') of the
                local time.
            start_date: A datetime object with the start date and time of the
                event. If not provided, None is assumed.

        Returns:
            A string with the appropriate recurrence, formatted as a cron
            expression.

        Raises:
            NotImplementedError: The original recurrence contains anything
            other than single hours or minutes (e.g., ranges). These are
            currently not supported by this implementation."""

        parsed_recurrence = parse_cron_expression(current_recurrence)

        # For the time being, we don't handle cron expressions which specify
        # anything but a specific hour and minute (i.e., ranges, multiple
        # hours, etc.). This is a feature that will be implemented in the
        # future.
        if not re.match(r'^\d+$', parsed_recurrence['hour']):
            raise NotImplementedError("This script cannot yet handle multiple hours in cron expressions: '{}'".format(current_recurrence))
        if not re.match(r'^\d+$', parsed_recurrence['minute']):
            raise NotImplementedError("This script cannot yet handle multiple minutes in cron expressions: '{}'".format(current_recurrence))

        # If the cron expression is not selective on the hour, it does not make
        # sense to keep going.
        if parsed_recurrence['hour'] == '*':
            print("Recurrence's cron expression ('{}') is not selective on the hour. Leaving recurrence as is.".format(current_recurrence))
            return current_recurrence

        utc_now = self._time_source.get_current_utc_datetime()

        # If the start date is over a day in the future, skip it. (We need to
        # reevaluate whether this logic belongs to this class.)
        if start_time and (start_time - utc_now).days > 1:
            print("Start date is over a day away. Leaving recurrence as is.")
            return current_recurrence

        # Determine when the event will run next, and compare the time with the
        # expected local time at the specified timezone. If they match, then
        # we're all good. If they don't, we need to update the recurrence.
        #
        # Note that we're adding one extra second to the time delta, to account
        # for precision errors which might produce incorrect results. (See for
        # example when the expected time is 14:00:00 and the delta causes us to
        # see 13:59:59.998). This is pretty hacky and I should revisit this,
        # for sure.

        recurrence = CronTab(current_recurrence)
        delta = timedelta(seconds = recurrence.next(default_utc=True) + 1)
        utc_next_run = utc_now + delta
        local_next_run = utc_next_run.astimezone(pytz.timezone(timezone))
        local_next_run_time = local_next_run.strftime('%H:%M')

        print("This event should run at '{}' local time. The next run will occur at '{}', which is '{}' at specified local timezone '{}'.".format(expected_time, utc_next_run.isoformat(), local_next_run_time, timezone))

        if local_next_run_time == expected_time:
            print("Times match. Current recurrence is correct.")
            return current_recurrence

        print("Times don't match. Current recurrence must be recalculated.")
        local_expected_run = local_next_run.replace(hour=parser.parse(expected_time).hour,
                                                    minute=parser.parse(expected_time).minute)
        utc_expected_run = local_expected_run.astimezone(pytz.timezone('UTC'))

        # We should only change the hour and minute parts of the cron
        # expression. The rest should be left as it was originally. The reason
        # we're changing the minutes too is because some timezones don't have
        # whole offsets. E.g., see "Indian Standard Time".
        new_recurrence = '{} {} {}'.format(utc_expected_run.minute,
                                           utc_expected_run.hour,
                                           parsed_recurrence['rest'])

        return new_recurrence
