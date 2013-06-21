from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
private_message = Table('private_message', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('sender_id', Integer),
    Column('recipient_id', Integer),
    Column('title', String(length=120)),
    Column('text', Text),
    Column('isRead', Boolean),
    Column('creation_time', DateTime),
    Column('parentID', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['private_message'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['private_message'].drop()
