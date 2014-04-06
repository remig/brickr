import re, datetime, bleach

bleach.ALLOWED_TAGS.extend([u'img', u'p', u'br'])
bleach.ALLOWED_ATTRIBUTES[u'img'] = [u'src', u'title']

def str_to_url(s):
    url = '_'.join(s.strip().lower().split())  # lower case and replace space with underscore
    url = re.sub('[^a-z0-9_]+', '', url)  # remove anything except letters, numbers and underscore
    return url

def now():
    return datetime.datetime.utcnow()
    
def roundFloat(f):  # In python < 3.0, round() still returns a float
    return int(round(float(f)))

def sanitizeHTML(s):
    return bleach.clean(s, strip=True)
    