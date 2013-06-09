import os
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
    
@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')
    
@app.route('/binaries/<username>/<filename>')
def uploaded_file(username, filename):
    return send_file(os.path.join('binaries', username, filename))
    
from app.users.views import mod as usersModule
app.register_blueprint(usersModule)

from app.photos.views import mod as photoModule
app.register_blueprint(photoModule)
