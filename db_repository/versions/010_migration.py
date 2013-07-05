from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('openid', String(length=200)),
    Column('name', String(length=50)),
    Column('email', String(length=120)),
    Column('password', String(length=20)),
    Column('role', SmallInteger, default=ColumnDefault(2)),
    Column('status', SmallInteger, default=ColumnDefault(1)),
    Column('creation_time', DateTime),
    Column('url', String(length=50)),
    Column('real_name', String(length=120)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['real_name'].create()
    post_meta.tables['user'].columns['url'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['real_name'].drop()
    post_meta.tables['user'].columns['url'].drop()
