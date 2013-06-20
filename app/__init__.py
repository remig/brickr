import os.path
from flask import Flask, render_template, g, session, send_file
from flask.ext.sqlalchemy import SQLAlchemy

def breakpoint():
    import pdb
    pdb.set_trace()

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app.models.user import User

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
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/')
def index():
    if g.user:
        photos = g.user.photos
        return render_template('photos/stream.html', user = g.user, photos = photos)
    return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/binaries/<filename>')
def binary_photo(filename):
    return send_file(os.path.join('binaries', filename))

from app.users.views import mod as usersModule
app.register_blueprint(usersModule)

from app.photos.views import mod as photoModule
app.register_blueprint(photoModule)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(os.path.join('logs', 'microblog.log'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')
