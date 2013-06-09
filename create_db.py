import os
os.environ['PYTHONINSPECT'] = 'True'

from app import db
db.create_all()
