# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

def get_tag_by_key(tags, key):
    tags = list(filter(lambda t: t['Key'] == key, tags))
    if len(tags):
    	return tags[0]['Value']
    return None
