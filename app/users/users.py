import os
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from werkzeug import check_password_hash, generate_password_hash
from flickrapi import FlickrAPI

from app import db, oid, breakpoint
from app.users.userForms import RegisterForm, LoginForm
from app.models import *
from app.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix = '/users')

@mod.route('/')
def root():
    return render_template('users/user_index.html', users = User.query.filter_by(placeholder = None).all())

@mod.route('/me/')
@requires_login
def home():
    return render_template('users/profile.html', user = g.user)

@mod.route('/login/', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())

    if request.method == 'POST':
        openid = request.form.get('openid_auto_url')
        if not openid:
            openid = request.form.get('openid')
        if openid:
            return oid.try_login(openid, ask_for = ['email', 'fullname', 'nickname', 'country', 'timezone', 'website'])

    # login form
    form = LoginForm(request.form)
    # make sure data is valid, but doesn't validate password is right
    if form.validate_on_submit():
        g.user = User.query.filter_by(email = form.email.data).first()
        #we use werzeug to validate user's password
        if g.user and check_password_hash(g.user.password, form.password.data):
            # the session can't be modified as it's signed, it's a safe place to store the user ID
            session['user_id'] = g.user.id
            flash('Successfully logged %s in!' % g.user.name)
            return redirect(oid.get_next_url())
        flash('Wrong email or password', 'error-message')
    return render_template('users/login.html', form = form, next = oid.get_next_url(), error = oid.fetch_error())
    
@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid = resp.identity_url).first()
    if user is None:
        return redirect(url_for('users.register', next = oid.get_next_url(),
                                 real_name = resp.fullname or resp.nickname,
                                 email = resp.email))  # Send new user to profile creation page

    # User successfully logged out - cache user object then redirect to wherever they came from
    g.user = user
    return redirect(oid.get_next_url())
    
@mod.route('/logout/')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    if 'openid' in session:
        session.pop('openid')
    flash('You were logged out')
    return redirect(oid.get_next_url())
    
@mod.route('/register/', methods = ['GET', 'POST'])
def register():
    if g.user is not None or 'openid' not in session:
        return redirect(oid.get_next_url())

    # Registration form
    form = RegisterForm(request.form)
    if 'openid' in session:
        form.password.validators = []
        form.confirm.validators = []

    if form.validate_on_submit():
        # Create a user instance not yet stored in the database
        user = User(form.screen_name.data, form.email.data, form.real_name.data)
        if 'openid' in session:
            user.openid = session['openid']
        else:
            user.password = generate_password_hash(form.password.data)

        if form.flickr_auth.data:  # User selected to authorize their screen name as a flickr account
            session['tmp_flickr_user'] = user;
            api_key = os.environ['PARAM1']
            api_secret = os.environ['PARAM2']
            flickr = FlickrAPI(api_key, api_secret, store_token = False)

            login_url = flickr.web_login_url('read')
            return redirect(login_url)
        else:
            # Insert the record in our data base and commit it
            db.session.add(user)
            db.session.commit()

            # Log the user in, as he now has an ID
            session['user_id'] = user.id
    
        flash('Thank you for registering with Brickr!')
        return redirect(url_for('index'))  # Send newly minted user to their Brickr landing page
    return render_template('users/register.html', form = form, next = oid.get_next_url())

# This URL is hit by flickr itself after user has successfully authenticated
@mod.route('/flickr_auth/', methods = ['GET', 'POST'])
def flickr_auth():
    # Convert the frob passed back from Flickr's auth system into an auth token.
    api_key = os.environ['PARAM1']
    api_secret = os.environ['PARAM2']
    flickr = FlickrAPI(api_key, api_secret, store_token = False)
    token = flickr.get_token(request.values['frob'])

    # Retrieve the Flickr screen name associated with the dude that just authenticated
    rsp = flickr.auth_checkToken(auth_token = token, format = 'xmlnode')
    flickr_screen_name = rsp.auth[0].user[0].attrib['username']

    user = session['tmp_flickr_user'];
    
    # Check if authenticated screen name matches screen name entered on account creation
    if flickr_screen_name.lower() == user.name.lower():
        user.flickr_auth = True
        db.session.add(user)
        db.session.commit()
        flash('You have successfully authenticated your Flickr account.  Welcome.')
        return redirect(url_for('index'))  # Send newly minted user to their Brickr landing page
    else:
        flash('Your chosen Screen Name does not match the Screen Name you logged into Flickr with!  Try this one.')
        db.session.rollback()
        return redirect(url_for('users.register', next = oid.get_next_url(),
                                do_flickr_auth = True,
                                screen_name = flickr_screen_name,
                                real_name = user.real_name,
                                email = user.email))  # Send user back to profile creation page
    return 'FAILED to Authenticate with Flickr.  FAILED.  HARD.  Call Remi.'

@mod.route('/_addContact/', methods = ['POST'])
@requires_login
def addContact():
    if request.method == 'POST':
        userID = request.form.get('userID')
        user = User.query.get(userID)
        if user and Contact.query.filter_by(user_id = g.user.id, target_user_id = userID).count() < 1:
            contact = Contact(g.user, user)
            db.session.add(contact)
            db.session.commit()
            return jsonify(result = True)
    return jsonify(result = False)

@mod.route('/_removeContact/', methods = ['POST'])
@requires_login
def removeContact():
    if request.method == 'POST':
        userID = request.form.get('userID')
        user = User.query.get(userID)
        contact = Contact.query.filter_by(user_id = g.user.id, target_user_id = userID)
        if user and contact.count() > 0:
            db.session.delete(contact.first())
            db.session.commit()
            return jsonify(result = True)
    return jsonify(result = False)
