import os, sys

PRODUCTION = True  # change this to False when developing locally

if not PRODUCTION:
    import brickr_keys

BASEDIR = os.path.abspath(os.path.dirname(__file__))

APPLICATION_NAME = 'brickr'

if PRODUCTION:  # AWS production config

    if 'RDS_HOSTNAME' not in os.environ or 'AWS_ACCESS_KEY_ID' not in os.environ:
        print "\n*** ERROR: Could not find AWS RDS hostname - if you're running this locally, edit config.py: switch 'PRODUCTION' to False.  If this is a production deploy, well, you're hosed.\n"
        sys.exit()

    SQLALCHEMY_DATABASE_URI = 'mysql://' + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] +'@' + os.environ['RDS_HOSTNAME']  + '/' + os.environ['RDS_DB_NAME']
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')

    S3_LOCATION = 'http://s3-us-west-1.amazonaws.com'
    S3_BUCKET = 'elasticbeanstalk-us-west-1-001101967776'
    S3_UPLOAD_DIRECTORY = APPLICATION_NAME

    S3_KEY = os.environ['AWS_ACCESS_KEY_ID']
    S3_SECRET = os.environ['AWS_SECRET_KEY']

    DEBUG = False
    TESTING = False

else:  # Local config

    DATABASE_NAME = 'app.db'
    DATABASE_FILENAME = os.path.join(BASEDIR, DATABASE_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILENAME
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')
    DATABASE_CONNECT_OPTIONS = {}

    IMG_URL_PATH = '/binaries/img'
    BINARY_URL_PATH = '/binaries'
    BINARY_PATH = os.path.join(BASEDIR, 'app', 'binaries')

    DEBUG = True
    TESTING = False

# Settings common to all deployments
SECRET_KEY = os.environ['PARAM3']
ADMINS = frozenset(['remigagne@gmail.com'])
THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = os.environ['PARAM4']

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = 'doom'
RECAPTCHA_PRIVATE_KEY = os.environ['PARAM5']
RECAPTCHA_OPTIONS = {'theme': 'white'}
