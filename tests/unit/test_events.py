# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import boto3
from botocore.stub import Stubber
from lib.events import EventBus
import pytest


def test_emit_process_completed():
    mocked_response = {
        'FailedEntryCount': 0,
        'Entries': [
            {
                'EventId': '00000000-0000-0000-0000-000000000000'
            }
        ]
    }
    expected_params = {
        'Entries': [
            {
                'Source': 'scheduled-event-adjuster',
                'DetailType': 'ProcessCompleted',
                'Detail': '{"Updates": [{"foo": "bar"}]}',
                'EventBusName': 'default'
            }
        ]
    }
    eventbridge_client = boto3.client('events')
    stubber = Stubber(eventbridge_client)
    stubber.add_response('put_events', mocked_response, expected_params)
    bus = EventBus(eventbridge_client)

    with stubber:
        response = bus.emit_process_completed([{'foo': 'bar'}])
        assert response == mocked_response
