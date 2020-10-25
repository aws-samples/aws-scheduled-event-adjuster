import json

class Event:
    PROCESS_COMPLETED = 'ProcessCompleted'

class EventBus:
    SOURCE = 'scheduled-scaling-adjuster'
    BUS_NAME = 'default'

    def __init__(self, eventbridge_client):
        self._eventbridge_client = eventbridge_client

    def emit_process_completed(self, updates):
        return self._eventbridge_client.put_events(
            Entries=[
                {
                    'Source': self.SOURCE,
                    'DetailType': Event.PROCESS_COMPLETED,
                    'Detail': json.dumps({'Updates': updates}),
                    'EventBusName': self.BUS_NAME
                }
            ]
        )
