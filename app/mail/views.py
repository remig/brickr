from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from app import db, breakpoint, strip
from app.models import *
from app.users.decorators import requires_login

mod = Blueprint('mail', __name__, url_prefix = '/mail')

@mod.route('/')
@requires_login
def inbox():
    messages = PrivateMessage.query.filter_by(recipient_id = g.user.id)
    sent_messages = PrivateMessage.query.filter_by(sender_id = g.user.id)
    return render_template('mail/inbox.html', user = g.user, messages = messages, sent_messages = sent_messages)

@mod.route('/<messageID>')
@requires_login
def message(messageID):
    message = PrivateMessage.query.get(messageID)
    message.isRead = True
    db.session.commit()
    return render_template('mail/message.html', message = message)

@mod.route('/compose/')
@requires_login
def compose():
    return render_template('mail/compose.html')

@mod.route('/_sendMessage', methods = ['POST'])
@requires_login
def sendMessage():
    if request.method == 'POST':
        recipient_name = strip(request.form.get('recipient'))
        subject = strip(request.form.get('subject'))
        text = strip(request.form.get('text'))
        
        recipient = User.query.filter_by(name = recipient_name).first()
        
        if recipient is None:
            flash(u'Could not find user: %s ' % (recipient_name))
            return redirect(url_for('mail.compose'))
            
        if not subject:
            flash(u'Cannot send a message with no title')
            return redirect(url_for('mail.compose'))

        if not text:
            flash(u'Cannot send a message with an empty body')
            return redirect(url_for('mail.compose'))

        msg = PrivateMessage(g.user, recipient, subject, text)
        db.session.add(msg)
        db.session.commit()
        flash(u'Message Sent!')
    return redirect(url_for('mail.inbox'))
