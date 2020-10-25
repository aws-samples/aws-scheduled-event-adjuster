#!/bin/bash

aws events put-events \
	--entries '[
		{
			"EventBusName": "default",
			"Source": "scheduled-scaling-adjuster",
			"DetailType": "ManualTrigger",
			"Detail": "{}"
		}
	]' | jq .
