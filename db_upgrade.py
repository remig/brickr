from migrate.versioning import api
from app import app, db, breakpoint

SQLALCHEMY_DATABASE_URI = app.config['SQLALCHEMY_DATABASE_URI']
SQLALCHEMY_MIGRATE_REPO = app.config['SQLALCHEMY_MIGRATE_REPO']

api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))