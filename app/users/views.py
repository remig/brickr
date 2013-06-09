from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash

from app import db, breakpoint
from app.users.forms import RegisterForm, LoginForm
from app.models import *
from app.users.decorators import requires_login

mod = Blueprint('users', __name__, url_prefix = '/users')

@mod.route('/me/')
@requires_login
def home():
    return render_template('users/profile.html', user = g.user)
    
@mod.before_request
def before_request():
    # pull user's profile form the database before every request is treated
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])
        
@mod.route('/login/', methods = ['GET', 'POST'])
def login():
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
            if form.nextURL:
                return redirect(form.nextURL.data)
            else:
                return redirect(url_for('users.home'))
        flash('Wrong email or password', 'error-message')
    return render_template('users/login.html', form = form, nextURL = request.args.get('next'))
    
@mod.route('/logout/')
def logout():
    session.pop('user_id')
    flash('You were logged out')
    return redirect(url_for('index'))
    
@mod.route('/register/', methods = ['GET', 'POST'])
def register():
    # Registration form
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # Create a user instance not yet stored in the database
        user = User(form.name.data, form.email.data, generate_password_hash(form.password.data))
        # Insert the record in our data base and commit it
        db.session.add(user)
        db.session.commit()
        
        # Log the user in, as he hnow has an ID
        session['user_id'] = user.id
        
        # flash will display a message to the user
        flash('Thanks for registering')
        
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('users.home'))
    return render_template('users/register.html', form = form)
    
@mod.route('/addContact/', methods = ['POST'])
@requires_login
def addContact():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(name = username).first()
        if user and Contact.query.filter_by(user_id = g.user.id, target_user_id = user.id).count() < 1:
            contact = Contact(g.user, user)
            db.session.add(contact)
            db.session.commit()
            flash('Successfully added %s as a contact' % user.name)
        return redirect(url_for('photos.stream', username = user.name))

