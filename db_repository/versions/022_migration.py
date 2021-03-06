from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
group_photo_list = Table('group_photo_list', post_meta,
    Column('photo_id', Integer, primary_key=True, nullable=False),
    Column('group_id', Integer, primary_key=True, nullable=False),
    Column('add_time', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['group_photo_list'].columns['add_time'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['group_photo_list'].columns['add_time'].drop()
