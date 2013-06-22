from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
group = Table('group', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String, nullable=False),
    Column('url_name', String, nullable=False),
    Column('description', Text),
    Column('rules', Text),
    Column('creation_time', DateTime),
)

group_tbl = Table('group_tbl', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=60), nullable=False),
    Column('url_name', String(length=60), nullable=False),
    Column('description', Text),
    Column('rules', Text),
    Column('creation_time', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['group'].drop()
    post_meta.tables['group_tbl'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['group'].create()
    post_meta.tables['group_tbl'].drop()
