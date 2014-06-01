import re
from flask import *
from app import db, oid, breakpoint, strip
from app.models import *

from app.decorators import requires_login

mod = Blueprint('api', __name__, url_prefix = '/api')

#@mod.app_errorhandler(404):
#def not_found(error):
#   return make_response(jsonify( { 'error': 'Not found' } ), 404)

@mod.route('/p/<photoID>/')
def get_photo(photoID):
    photo = Photo.query.get(photoID)
    if photo is None:
        abort(404)

    return jsonify(photo.to_json())
    
@mod.route('/u/<userID>/photos/')
def get_user_photos(userID):
    if (userID == '-1' and g.user):
        user = g.user
    else:
        user = User.query.get(userID)
    if user is None or user.placeholder:
        abort(404)

    if 'from_contacts' in request.args:
        photos = user.get_contacts_photo_list(int(request.args.get('count', 10)))
        return jsonify({'userID': userID, 'is_contact_list': True, 'photos': [p.to_json() for p in photos]})
    else:
        return jsonify({'userID': userID, 'photos': [p.to_json() for p in user.photos]})

@mod.route('/u/<userID>/groups/')
def get_user_groups(userID):
    if (userID == '-1' and g.user):
        user = g.user
    else:
        user = User.query.get(userID)
    if user is None or user.placeholder:
        abort(404)
        
    return jsonify({'userID': user.id, 'username': user.name, 'groups': [group.to_json() for group in user.user_groups]})

@mod.route('/<groupURL>/')
def group(groupURL):
    group = Group.query.filter_by(url_name = groupURL).first()
    groupJSON = group.to_json()
    groupJSON['members'] = [x.to_json() for x in group.members]
    groupJSON['photos'] = [x.photo.to_json() for x in group.photo_groups]
    return render_template('groups/group.html', group = group, groupJSON = json.dumps(groupJSON))
    
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
            photo_group = photo.getGroupAssoc(group)
            if photo and doAdd and photo_group is None:
                GroupPhotoList(photo, group)
            elif not doAdd and photo_group:
                db.session.delete(photo_group)
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
                GroupMemberList(user, group)
            elif action == 'leave' and user in group.members:
                group.members.remove(user)  # TODO: fix this!!
            db.session.commit()
        return jsonify(result = True)
    return jsonify(result = False)

@mod.route('/<groupURL>/discussion/<discussionID>')
def discussion(groupURL, discussionID):
    group = Group.query.filter_by(url_name = groupURL).first()
    discussion = Discussion.query.get(discussionID)
    return render_template('groups/discussion.html', group = group, discussion = discussion)

@mod.route('/<groupURL>/new_topic/', methods = ['GET', 'POST'])
@requires_login
def createDiscussion(groupURL):
    group = Group.query.filter_by(url_name = groupURL).first()
    if request.method == 'POST':

        title = request.form.get('title')
        post_text = request.form.get('post_text')

        discussion = Discussion(group, title)
        db.session.add(discussion)
        db.session.commit()  # must commit discussion before creating post, so that discussion has valid ID

        post = DiscussionPost(discussion, g.user, post_text)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('groups.discussion', groupURL = group.url_name, discussionID = discussion.id))
    return render_template('groups/new_discussion.html', group = group)

@mod.route('/_addPost/', methods = ['POST'])
@requires_login
def addDiscussuionPost():
    if request.method == 'POST':
        post_text = request.form.get('post_text')
        discussionID = request.form.get('discussionID')
        discussion = Discussion.query.get(discussionID)
        if discussion and post_text:
            post = DiscussionPost(discussion, g.user, post_text)
            db.session.add(post)
            db.session.commit()
        return redirect(url_for('groups.discussion', groupURL = discussion.group.url_name, discussionID = discussion.id))
