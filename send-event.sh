#!/bin/bash

aws events put-events \
	--entries '[
		{
			"EventBusName": "default",
			"Source": "scheduled-event-adjuster",
			"DetailType": "ManualTrigger",
			"Detail": "{}"
		}
	]' | jq .
