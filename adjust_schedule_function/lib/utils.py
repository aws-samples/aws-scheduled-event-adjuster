def get_tag_by_key(tags, key):
    tags = list(filter(lambda t: t['Key'] == key, tags))
    if len(tags):
    	return tags[0]['Value']
    return None
