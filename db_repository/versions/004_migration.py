from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
group = Table('group', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=60), nullable=False),
    Column('url_name', String(length=60), nullable=False),
    Column('description', Text),
    Column('rules', Text),
    Column('creation_time', DateTime),
)

group_member_list = Table('group_member_list', post_meta,
    Column('user_id', Integer),
    Column('group_id', Integer),
)

group_photo_list = Table('group_photo_list', post_meta,
    Column('photo_id', Integer),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['group'].create()
    post_meta.tables['group_member_list'].create()
    post_meta.tables['group_photo_list'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['group'].drop()
    post_meta.tables['group_member_list'].drop()
    post_meta.tables['group_photo_list'].drop()
