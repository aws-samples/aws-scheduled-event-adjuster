# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

class ResourceProcessor:
    def __init__(self, tag_prefix):
        self._tag_prefix = tag_prefix

    def _get_enabled_tag(self):
        """Returns the tag that, when present, determines whether a resource
        must be processed.
        """
        return '%s:%s' % (self._tag_prefix, 'enabled')

    def _get_local_timezone_tag(self):
        """Returns the tag that specifies the timezone of the local time.
        """
        return '%s:%s' % (self._tag_prefix, 'local-timezone')

    def _get_local_time_tag(self):
        """Returns the tag that specifies the local time at which scheduled
        events must run.
        """
        return '%s:%s' % (self._tag_prefix, 'local-time')
