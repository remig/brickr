import re
from flask import *
from app import db, oid, breakpoint, strip
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
    
pattern = re.compile('[^A-Za-z0-9_]+')
@mod.route('/create_group/', methods = ['GET', 'POST'])
@requires_login
def create_group():
    if request.method == 'POST':

        name = strip(request.form.get('name'))
        url_name = pattern.sub('', request.form.get('url_name'))
        desc = request.form.get('description')
        rules = request.form.get('rules')

        if Group.query.filter_by(name = name).count() > 0:
            flash(u'A Group with the name "%s" already exists - choose another.' % (name))
            return render_template('groups/create_group.html', name = name, url_name = url_name, description = desc, rules = rules)

        if Group.query.filter_by(url_name = url_name).count() > 0:
            flash(u'A Group with the short name "%s" already exists - choose another.' % (url_name))
            return render_template('groups/create_group.html', name = name, url_name = url_name, description = desc, rules = rules)

        group = Group(name, url_name, desc, rules)
        group.members.append(g.user)
        db.session.commit()
        return redirect(url_for('groups.group', groupURL = url_name))
    return render_template('groups/create_group.html')

@mod.route('/delete_group/<groupURL>', methods = ['GET', 'POST'])
@requires_login
def delete_group(groupURL):  # NYI
    return redirect(url_for('groups.group', groupURL = groupURL))
    
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
