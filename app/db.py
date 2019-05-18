import flask
import psycopg2
import psycopg2.extras
import config
import json
from .model import *
from app import db

def get_connection():
    if not hasattr(flask.g, 'dbconn'):
        flask.g.dbconn = psycopg2.connect(user=config.DATABASE_ADMIN, database=config.DATABASE_NAME, host=config.DATABASE_HOST, password=config.DATABASE_PASSWORD)
        return flask.g.dbconn
    else:
        return flask.g.dbconn

def get_cursor():
    return get_connection().cursor(cursor_factory=psycopg2.extras.DictCursor)


def query_one(sql, **params):
    with get_cursor() as cur:
        cur.execute(sql, params)
        return dict(cur.fetchone())


def query_all(sql, **params):
    with get_cursor() as cur:
        cur.execute(sql, params)
        result = cur.fetchall()
        return {i: dict(result[i]) for i in range(len(result))}

def get_users_list_by_mask(mask):
    q = User.query.filter(User.name.like('%{}%'.format(mask))).all()
    users = UserSchema(many=True)
    return users.dump(q).data

def get_chats_list():
    q = Chat.query.all()
    chats = ChatSchema(many=True)
    output = chats.dump(q).data
    return output


def get_members_list(user_id):
    q = Chat.query.join(Member).filter(Chat.id == Member.id).filter_by(user_id = user_id).all()
    chats = ChatSchema(many=True)
    return chats.dump(q).data

def add_new_chat(is_group_chat, topic):
    q = Chat(True if is_group_chat == "t" else False, topic, None)
    db.session.add(q)
    db.session.commit()
    return {'id': q.id}


    # t = query_all("""
	# 	INSERT INTO "Chat" (is_group, topic, last_message) VALUES (%(is_group_chat)s, %(topic)s, NULL)
	# 	RETURNING id;
	# """,
    #               is_group_chat=str(is_group_chat),
    #               topic=str(topic))
    # commit()
    # return t


def add_new_message(chat_id, user_id, content, sent):
    q = Message(chat_id, user_id, content, sent)
    db.session.add(q)
    db.session.commit()
    return {'id': q.id}


def add_new_file_message(chat_id, user_id, content, sent, filename, type, size):
    m = add_new_message(chat_id, user_id, content, sent)
    print(m)

    mid = m[0]['message_id']

    q = Attachment(chat_id, user_id, mid, type, filename, size)
    db.session.add(q)
    db.session.commit()
    return {'id': q.id}


#IT DOES NOT RETURN ATTACHMENTS
def get_messages(chat_id):
    q = Message.query.filter(Message.chat_id == chat_id).all()
    messages = MessageSchema(many=True)
    return messages.dump(q).data


def add_new_member_to_chat(user_id, chat_id):
    q = Member(chat_id, user_id, 0)
    db.session.add(1)
    db.session.commit()
    return {
        'id': q.id
    }


def check_user_existance(user_id):
    q = User.query.filter_by(id=user_id)
    users = UserSchema()
    return users.dump(q).data

def create_user(user_id, name, nick):
    q = User(user_id, nick, name)
    db.session.add(q)
    db.session.commit()
    return {
        'id': q.id
    }

def get_name_by_id(user_id):
    q = User.query.filter_by(id=user_id)
    users = UserSchema()
    return users.dump(q).data