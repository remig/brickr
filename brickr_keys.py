# These are very important and SECRET and should never be pushed to git or any
# other source control system.  This file is only for local use!
#
# For remote uses, these keys are duplicated in .elasticbeanstalk\optionsettings
#
# Key names are defined by AWS, which does not yet support custom environment variable names

import os

# Amazon Services keys - Only needed if you want to test S3 upload locally.  Get this from AWS.
os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_KEY'] = ''

# Flickr API keys - get these by requesting API keys from Flickr.
os.environ['PARAM1'] = ''  # Flickr API key
os.environ['PARAM2'] = ''  # Flickr API secret

# Make up whatever long, random string you want for these.
os.environ['PARAM3'] = ''  # Flask secret key
os.environ['PARAM4'] = ''  # CSRF_SESSION_KEY
os.environ['PARAM5'] = ''  # RECAPTCHA_PRIVATE_KEY