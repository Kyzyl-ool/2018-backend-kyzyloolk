# from .db import *
from app import app, db, ma
from datetime import datetime
import json


def to_json(inst, cls):
	"""
    Jsonify the sql alchemy query result.
    """
	convert = dict()
	# add your coversions for things like datetime
	# and what-not that aren't serializable.
	d = dict()
	for c in cls.__table__.columns:
		v = getattr(inst, c.name)
		if c.type in convert.keys() and v is not None:
			try:
				d[c.name] = convert[c.type](v)
			except:
				d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
		elif v is None:
			d[c.name] = str()
		else:
			d[c.name] = v
	return json.dumps(d)


class User(db.Model):
	__tablename__ = 'User'

	id = db.Column(db.Integer, primary_key=True)
	nick = db.Column(db.String(255), unique=True, nullable=False)
	name = db.Column(db.String(255), nullable=False)

	def __init__(self, id, nick, name):
		self.id = id
		self.nick = nick
		self.name = name

	def __repr__(self):
		return to_json(self, self.__class__)


class Message(db.Model):
	__tablename__ = 'Message'

	id = db.Column(db.Integer, primary_key=True)
	chat_id = db.Column(db.Integer, db.ForeignKey('Chat.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	content = db.Column(db.Text, nullable=False)
	sent = db.Column(db.DateTime, nullable=False)

	def __init__(self, chat_id, user_id, content, sent):
		if sent is None:
			self.sent = datetime.utcnow()
		else:
			self.sent = sent

		self.chat_id = chat_id
		self.user_id = user_id
		self.content = content

	def __repr__(self):
		return to_json(self, self.__class__)



class Attachment(db.Model):
	__tablename__ = 'Attachment'

	id = db.Column(db.Integer, primary_key=True)
	chat_id = db.Column(db.Integer, db.ForeignKey('Chat.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	message_id = db.Column(db.Integer, db.ForeignKey('Message.id'))
	type = db.Column(db.String(255), nullable=False)
	url = db.Column(db.String(255), nullable=False)
	size = db.Column(db.Integer, nullable=False)

	def __init__(self, chat_id, user_id, message_id, type, url, size):
		self.chat_id = chat_id
		self.user_id = user_id
		self.message_id = message_id
		self.type = type
		self.url = url
		self.size = size

	def __repr__(self):
		return to_json(self, self.__class__)


class Chat(db.Model):
	__tablename__ = 'Chat'

	id = db.Column(db.Integer, primary_key=True)
	is_group = db.Column(db.Boolean)
	topic = db.Column(db.String(255), nullable=False)
	last_message = db.Column(db.Integer, db.ForeignKey('Message.id'))

	def __init__(self, is_group, topic, last_message):
		self.is_group = is_group
		self.topic = topic
		self.last_message = last_message

	def __repr__(self):
		return to_json(self, self.__class__)


class Member(db.Model):
	__tablename__ = 'Member'

	id = db.Column(db.Integer, primary_key=True)
	chat_id = db.Column(db.Integer, db.ForeignKey('Chat.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	last_unread_message_id = db.Column(db.Integer, db.ForeignKey('Message.id'))

	def __init__(self, chat_id, user_id, last_unread_message_id):
		self.chat_id = chat_id
		self.user_id = user_id
		self.last_unread_message_id = last_unread_message_id

	def __repr__(self):
		return to_json(self, self.__class__)


class MessageSchema(ma.ModelSchema):
	class Meta:
		model = Message

class AttachmentSchema(ma.ModelSchema):
	class Meta:
		model = Attachment


class ChatSchema(ma.ModelSchema):
	class Meta:
		model = Chat

class MemberSchema(ma.ModelSchema):
	class Meta:
		model = Member

class UserSchema(ma.ModelSchema):
	class Meta:
		model = User