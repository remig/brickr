from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify
from werkzeug import check_password_hash, generate_password_hash

from app import db, oid, breakpoint
from app.users.forms import RegisterForm, LoginForm
from app.models import *
from app.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix = '/users')

@mod.route('/')
def root():
    return render_template('users/user_index.html', users = User)

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
            return oid.try_login(openid, ask_for = ['email', 'fullname', 'nickname'])

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
                                 name = resp.fullname or resp.nickname,
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
        user = User(form.name.data, form.email.data)
        if 'openid' in session:
            user.openid = session['openid']
        else:
            user.password = generate_password_hash(form.password.data)

        # Insert the record in our data base and commit it
        db.session.add(user)
        db.session.commit()
        
        # Log the user in, as he hnow has an ID
        session['user_id'] = user.id
        
        # flash will display a message to the user
        flash('Thank you for registering with Brickr!')
        
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('users.home'))
    return render_template('users/register.html', form = form, next = oid.get_next_url())

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
