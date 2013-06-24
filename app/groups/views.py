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

@mod.route('/_leaveOrJoinGroup/', methods = ['POST'])
@requires_login
def leaveOrJoinGroup():
    if flask.request.method == 'POST':
        user = User.query.get(flask.request.form.get('userID'))
        group = Group.query.get(flask.request.form.get('groupID'))
        action = flask.request.form.get('action')
        if user and group:
            if action == 'join':
                group.members.append(user)
            elif action == 'leave' and user in group.members:
                group.members.remove(user)
            db.session.commit()
        return flask.jsonify(result = True)
    return flask.jsonify(result = False)
