#!/bin/bash
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

aws events put-events \
	--entries '[
		{
			"EventBusName": "default",
			"Source": "scheduled-event-adjuster",
			"DetailType": "ManualTrigger",
			"Detail": "{}"
		}
	]' | jq .
