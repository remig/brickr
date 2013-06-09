Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> import flickrapi
>>> api_key = 73c1ba64438081068a8aceeb85ffc7e4
SyntaxError: invalid syntax
>>> api_key = '73c1ba64438081068a8aceeb85ffc7e4'
>>> flickr = flickrapi.FlickrAPI(api_key)
>>> flickr.photos_getInfo(photo_id='8756063302')
<Element 'rsp' at 0x27cb810>
>>> x = flickr.photos_getInfo(photo_id='8756063302')
>>> x
<Element 'rsp' at 0x27ebfb0>
>>> x = flickr.photos_getInfo(photo_id='8756063302', format='json')
>>> x
'jsonFlickrApi({"photo":{"id":"8756063302", "secret":"1c0ee06cde", "server":"5463", "farm":6, "dateuploaded":"1369011047", "isfavorite":0, "license":"3", "safety_level":"0", "rotation":0, "originalsecret":"7f77d8e6ce", "originalformat":"jpg", "owner":{"nsid":"69691418@N00", "username":"Bolt of Blue", "realname":"Alyse & Remi", "location":"Los Angeles, USA", "iconserver":"3783", "iconfarm":4, "path_alias":"boltofblue"}, "title":{"_content":"Mark Hamill"}, "description":{"_content":"After the screening of Return of the Jedi, Mark Hamill was a surprise guest for an entertaining and charming Q&amp;A."}, "visibility":{"ispublic":1, "isfriend":0, "isfamily":0}, "dates":{"posted":"1369011047", "taken":"2013-05-04 20:49:39", "takengranularity":"0", "lastupdate":"1369097765"}, "views":"18", "editability":{"cancomment":0, "canaddmeta":0}, "publiceditability":{"cancomment":1, "canaddmeta":1}, "usage":{"candownload":1, "canblog":0, "canprint":0, "canshare":1}, "comments":{"_content":"4"}, "notes":{"note":[]}, "people":{"haspeople":0}, "tags":{"tag":[{"id":"2463216-8756063302-173512", "author":"69691418@N00", "raw":"Egyptian Theatre", "_content":"egyptiantheatre", "machine_tag":0}, {"id":"2463216-8756063302-460285", "author":"69691418@N00", "raw":"Mark Hamill", "_content":"markhamill", "machine_tag":0}, {"id":"2463216-8756063302-735707", "author":"69691418@N00", "raw":"ROTJ", "_content":"rotj", "machine_tag":0}, {"id":"2463216-8756063302-108869", "author":"69691418@N00", "raw":"Return of the Jedi", "_content":"returnofthejedi", "machine_tag":0}, {"id":"2463216-8756063302-2415", "author":"69691418@N00", "raw":"Star Wars", "_content":"starwars", "machine_tag":0}]}, "urls":{"url":[{"type":"photopage", "_content":"http:\\/\\/www.flickr.com\\/photos\\/boltofblue\\/8756063302\\/"}]}, "media":"photo"}, "stat":"ok"})'
>>> type x
SyntaxError: invalid syntax
>>> type(x)
<type 'str'>
>>> y = x = flickr.photos_comments_getList(photo_id='8756063302', format='json')
>>> y
'jsonFlickrApi({"comments":{"photo_id":"8756063302", "comment":[{"id":"2463216-8756063302-72157633523695739", "author":"43378406@N08", "authorname":"Si-MOCs", "iconserver":"3719", "iconfarm":4, "datecreate":"1369021110", "permalink":"http:\\/\\/www.flickr.com\\/photos\\/boltofblue\\/8756063302\\/#comment72157633523695739", "_content":"Did he do the Joker voice? XD"}, {"id":"2463216-8756063302-72157633533525987", "author":"69691418@N00", "authorname":"Bolt of Blue", "iconserver":"3783", "iconfarm":4, "datecreate":"1369093130", "permalink":"http:\\/\\/www.flickr.com\\/photos\\/boltofblue\\/8756063302\\/#comment72157633533525987", "_content":"[http:\\/\\/www.flickr.com\\/photos\\/si-mocs] yes, actually he did the laugh"}, {"id":"2463216-8756063302-72157633549853054", "author":"43378406@N08", "authorname":"Si-MOCs", "iconserver":"3719", "iconfarm":4, "datecreate":"1369095084", "permalink":"http:\\/\\/www.flickr.com\\/photos\\/boltofblue\\/8756063302\\/#comment72157633549853054", "_content":"[http:\\/\\/www.flickr.com\\/photos\\/boltofblue] ... really? haha I was totally making a jackass comment. But  that\'s so awesome, I have to move haha."}, {"id":"2463216-8756063302-72157633534676093", "author":"69691418@N00", "authorname":"Bolt of Blue", "iconserver":"3783", "iconfarm":4, "datecreate":"1369097765", "permalink":"http:\\/\\/www.flickr.com\\/photos\\/boltofblue\\/8756063302\\/#comment72157633534676093", "_content":"[http:\\/\\/www.flickr.com\\/photos\\/si-mocs] he did talk about how he doesn\'t like to do the voice in person... but if a kid asks him, he\'ll tell the kid to turn around first to not ruin the illusion."}]}, "stat":"ok"})'
>>> x = flickr.photos_getInfo(photo_id='8756063302')
>>> x
<Element 'rsp' at 0x27eec90>
>>> x.attrib['photo']

Traceback (most recent call last):
  File "<pyshell#15>", line 1, in <module>
    x.attrib['photo']
KeyError: 'photo'
>>> x.attrib
{'stat': 'ok'}
>>> x.items
<bound method Element.items of <Element 'rsp' at 0x27eec90>>
>>> 
>>> x.items()
[('stat', 'ok')]
>>> x.find('photo')
<Element 'photo' at 0x27eedf0>
>>> x.find('photo').attrib['comments']

Traceback (most recent call last):
  File "<pyshell#21>", line 1, in <module>
    x.find('photo').attrib['comments']
KeyError: 'comments'
>>> x.find('photo').attrib
{'originalsecret': '7f77d8e6ce', 'isfavorite': '0', 'license': '3', 'views': '18', 'farm': '6', 'media': 'photo', 'server': '5463', 'dateuploaded': '1369011047', 'secret': '1c0ee06cde', 'safety_level': '0', 'originalformat': 'jpg', 'rotation': '0', 'id': '8756063302'}
>>> 


Python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> from flask import Flask
>>> from flask.ext.sqlalchemy import SQLAlchemy
>>> app = Flask('doooooom')
>>> app.config('SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testX.db'
SyntaxError: invalid syntax
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testX.db'
>>> db = SQLAlchemy(app)
>>> class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)
	def __init__(self, username, email):
		self.username = username
		self.email = email
	def __repr__(self):
		return '<User %r>' % self.username

	
>>> db.create_all()
>>> admin = User('admin', 'a@b.c')
>>> guest = User('guest', 'g@c.d')
>>> db.session.add(admin)
>>> db.session.add(guest)
>>> db.session.commit()
>>> users = User.query.all()
>>> users
[<User u'admin'>, <User u'guest'>]
>>> admin = User.query.filter_by(username='admin')
>>> admin
<flask_sqlalchemy.BaseQuery object at 0x032F08B0>
>>> admin.first()
<User u'admin'>
>>> exit()