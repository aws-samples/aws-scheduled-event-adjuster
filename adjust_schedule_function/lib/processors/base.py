class ResourceProcessor:
	# The tag that determines whether the resource should be processed.
    ENABLED_TAG = 'scheduled-event-adjuster:enabled'

    # The tag that determines the timezone of the local time.
    LOCAL_TIMEZONE_TAG = 'scheduled-event-adjuster:local-timezone'

    # The tag that determines the local time at which the scheduled event is
    # expected to run.
    LOCAL_TIME_TAG = 'scheduled-event-adjuster:local-time'
