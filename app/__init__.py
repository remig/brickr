import os.path, re
from flask import Flask, render_template, g, session, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID

from flickrapi import FlickrAPI
import logging
for handler in logging.root.handlers:  # flickrapi sets up basic logging, which hoses flask logging
    logging.root.removeHandler(handler)

def breakpoint(): # pragma: no cover
    if app.debug:
        import pdb
        pdb.set_trace()

pattern = re.compile('[^A-Za-z0-9 _!$]+')  # TODO: move this to util
def strip(text):
    return pattern.sub('', text)

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

oid = OpenID(app)

from app.models import *

app.jinja_env.trim_blocks = True

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        g.user = User.query.filter_by(openid = session['openid']).first()
    elif 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/')
def index():
    if g.user:
        return render_template('dashboard/dashboard.html')
    return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/binaries/<path:filename>/')
def binary_photo(filename):
    return send_file(os.path.join('binaries', filename))

from app.views.users import mod as usersModule
app.register_blueprint(usersModule)

from app.views.photos import mod as photoModule
app.register_blueprint(photoModule)

from app.views.mail import mod as mailModule
app.register_blueprint(mailModule)

from app.views.groups import mod as groupModule
app.register_blueprint(groupModule)

from app.views.contests import mod as contestModule
app.register_blueprint(contestModule)

from app.views.api import mod as apiModule
app.register_blueprint(apiModule)

if not app.debug:
    import logging
    path = 'logs'
    if not os.path.exists(path):
        os.makedirs(path)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(os.path.join(path, 'brickr_errors.log'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('brickr startup')
