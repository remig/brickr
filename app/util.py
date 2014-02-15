import re

def str_to_url(s):
    url = '_'.join(s.strip().lower().split())  # lower case and replace space with underscore
    url = re.sub('[^a-z0-9_]+', '', url)  # remove anything except letters, numbers and underscore
    return url
