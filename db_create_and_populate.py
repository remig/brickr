import sys, os.path
from app import app, db, breakpoint
from app.models import *

if 'RDS_HOSTNAME' in os.environ:
    print "This init script is only useful for local sqlite databases, not RDS!"
    sys.exit()

if os.path.exists(app.config['DATABASE_FILENAME']):
    s = raw_input("Database already exisits - replace it? (y/n):")
    if s.lower()[0] == 'y':
        os.unlink(app.config['DATABASE_FILENAME'])
    else:
        sys.exit()

db.create_all()

sql = """
INSERT INTO "user" VALUES(1,NULL,'Remi','remigagne@gmail.com','sha1$yD3O4AaG$e7b1388b1a1ace1a04bc841b82ab54f8b7e82fd2',2,1,'2013-06-03 01:30:20.541000');
INSERT INTO "user" VALUES(2,NULL,'doom','doom@doom.com','sha1$1sLMWqRg$78d03095974d4dee0ba5c90db1bbc16e3c0f38d4',2,1,'2013-06-04 01:30:20.541000');
INSERT INTO "user" VALUES(3,NULL,'Bob','bob@xyz.com','sha1$1sLMWqRg$78d03095974d4dee0ba5c90db1bbc16e3c0f38d4',2,1,'2013-06-05 01:30:20.541000');
INSERT INTO "user" VALUES(4,NULL,'Alyse','alyse@abc.com','sha1$4QCeTPHy$d0c1cb4dc9ca2833e77dc8e0645f34230badf393',2,1,'2013-06-06 01:30:20.541000');
INSERT INTO "user" VALUES(5,NULL,'R2','remig@threedgraphics.com',NULL,2,1,'2013-06-22 19:52:18.672000');

INSERT INTO "photo" VALUES(1,1,'flickr-IMG_1811.jpg','Description text goes here',318,'2013-06-03 01:29:03.680000','.jpg');
INSERT INTO "photo" VALUES(2,1,'flickr-IMG_1812.jpg','Description text goes here',111,'2013-06-03 01:30:21.519000','.jpg');
INSERT INTO "photo" VALUES(3,2,'flickr-IMG_1845.jpg','Description text goes here',34,'2013-06-03 23:30:24.048000','.jpg');
INSERT INTO "photo" VALUES(4,4,'ele.jpg','Description text goes here',131,'2013-06-19 00:15:53.417000','.jpg');
INSERT INTO "photo" VALUES(5,1,'baxter.jpg','Description text goes here',55,'2013-06-19 03:00:53.877000','.jpg');

INSERT INTO "favorite" VALUES(1,2,1,'2013-06-03 22:59:19.607000');
INSERT INTO "favorite" VALUES(2,2,3,'2013-06-03 23:30:53.669000');
INSERT INTO "favorite" VALUES(3,3,1,'2013-06-15 02:34:35.529000');
INSERT INTO "favorite" VALUES(4,2,4,'2013-06-19 02:43:52.367000');
INSERT INTO "favorite" VALUES(5,1,1,'2013-06-20 16:28:24.048000');

INSERT INTO "comment" VALUES(1,1,1,'Hello!!!','2013-06-03 04:10:29.726000',NULL);
INSERT INTO "comment" VALUES(2,1,1,'DOOOOM','2013-06-03 04:11:18.690000',NULL);
INSERT INTO "comment" VALUES(3,1,1,'Yet another comment test','2013-06-03 04:46:54.382000',NULL);
INSERT INTO "comment" VALUES(4,2,1,'Comment from Doom?','2013-06-03 22:57:37.855000',NULL);
INSERT INTO "comment" VALUES(5,2,3,'Beautiful shot','2013-06-03 23:30:46.179000',NULL);

INSERT INTO "contact" VALUES(1,2,1,'2013-06-04 00:27:29.351000',1);
INSERT INTO "contact" VALUES(3,2,3,'2013-06-19 02:43:07.537000',0);
INSERT INTO "contact" VALUES(4,2,4,'2013-06-19 02:43:26.291000',0);

INSERT INTO "tag" VALUES(4,'ABCDEFG');
INSERT INTO "tag" VALUES(3,'Another Tag');
INSERT INTO "tag" VALUES(7,'DOOM');
INSERT INTO "tag" VALUES(2,'Hello!');
INSERT INTO "tag" VALUES(9,'LEGO');
INSERT INTO "tag" VALUES(8,'Link Shield');
INSERT INTO "tag" VALUES(1,'TAGME');
INSERT INTO "tag" VALUES(5,'abcd');
INSERT INTO "tag" VALUES(6,'def space');

INSERT INTO "tag_list" VALUES(1,1);
INSERT INTO "tag_list" VALUES(2,1);
INSERT INTO "tag_list" VALUES(3,1);
INSERT INTO "tag_list" VALUES(4,1);
INSERT INTO "tag_list" VALUES(5,1);
INSERT INTO "tag_list" VALUES(6,1);
INSERT INTO "tag_list" VALUES(7,1);
INSERT INTO "tag_list" VALUES(8,2);
INSERT INTO "tag_list" VALUES(9,2);

INSERT INTO "private_message" VALUES(1,2,1,'HELLO!','THIS WORKS??',0,'2013-06-21 00:11:41.482000',NULL);
INSERT INTO "private_message" VALUES(2,2,1,'HELLO AGAIN!!','Second Message of Goodness',0,'2013-06-21 00:13:10.557000',NULL);
INSERT INTO "private_message" VALUES(3,2,1,'Third Message','Getting Redundant around here...',0,'2013-06-21 00:14:53.386000',NULL);
INSERT INTO "private_message" VALUES(4,1,2,'Test first real message','Hi how are you today',0,'2013-06-21 01:28:14.389000',NULL);

INSERT INTO "group_tbl" VALUES(1,'Brickrs first Group','brickr_first_group','This is Brickr''s first group - enjoy, and join up!','There are no rules.','2013-06-21 16:57:14.695000');
"""

for line in sql.split(';'):
    db.session.execute(line.strip())

db.session.commit()
