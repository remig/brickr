from flask import *
from app import app, db, breakpoint, strip
from app.models import *

from app.users.decorators import requires_login

mod = Blueprint('groups', __name__, url_prefix = '/groups')

@mod.route('/')
def root():
    return render_template('groups/group_index.html', groups = Group)

@mod.route('/<groupURL>/')
def group(groupURL):
    group = Group.query.filter_by(url_name = groupURL).first()
    return render_template('groups/group.html', group = group)

@mod.route('/<groupURL>/add_photos/', methods = ['GET', 'POST'])
@requires_login
def add_photos(groupURL):
    group = Group.query.filter_by(url_name = groupURL).first()
    if request.method == 'POST' and group:
        doAdd = request.form.get('action') == 'add'
        for photo in [Photo.query.get(p) for p in request.form.keys() if p != 'action']:
            if photo and doAdd and photo not in group.photos:
                group.photos.append(photo)
            elif not doAdd and photo in group.photos:
                group.photos.remove(photo)
        db.session.commit()
        return redirect(url_for('groups.group', groupURL = groupURL))
    return render_template('groups/add_photo.html', group = group)

@mod.route('/_leaveOrJoinGroup/', methods = ['POST'])
@requires_login
def leaveOrJoinGroup():
    if request.method == 'POST':
        user = User.query.get(request.form.get('userID'))
        group = Group.query.get(request.form.get('groupID'))
        action = request.form.get('action')
        if user and group:
            if action == 'join':
                group.members.append(user)
            elif action == 'leave' and user in group.members:
                group.members.remove(user)
            db.session.commit()
        return jsonify(result = True)
    return jsonify(result = False)
