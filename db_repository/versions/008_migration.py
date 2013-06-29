from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
discussion_post = Table('discussion_post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('discussion_id', Integer),
    Column('user_id', Integer),
    Column('parent_id', Integer),
    Column('post', Text),
    Column('creation_time', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['discussion_post'].columns['post'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['discussion_post'].columns['post'].drop()
