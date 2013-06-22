import flask

from app import app, db, breakpoint, strip
from app.models import *

from app.users.decorators import requires_login

mod = flask.Blueprint('groups', __name__, url_prefix = '/groups')

@mod.route('/')
def root():
    return flask.render_template('groups/group_index.html', groups = Group)

@mod.route('/<groupURL>/')
def one_group(groupURL):
    group = Group.query.filter_by(url_name = groupURL).first()
    return flask.render_template('groups/group.html', group = group)
