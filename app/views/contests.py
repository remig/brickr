from flask import *
from app import db, breakpoint
from app.models import *

from app.decorators import requires_login

mod = Blueprint('contests', __name__, url_prefix = '/contests')

@mod.route('/')
def root():
    return render_template('contests/index.html')
    