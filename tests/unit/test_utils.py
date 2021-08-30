import pytest

from lib import utils

def test_get_tag_by_key():
    tags = [{'Key': 'foo', 'Value': 'bar'}, {'Key': 'baz', 'Value': 'quux'}]

    assert utils.get_tag_by_key(tags, 'foo') == 'bar'
    assert utils.get_tag_by_key(tags, 'nope') == None
