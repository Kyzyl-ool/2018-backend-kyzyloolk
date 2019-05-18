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
    # q = Message(chat_id, user_id, content, sent)
    # db.session.add(q)
    # db.session.commit()
    # return {'id': q.id}
    return {'code': 200}

    # t = query_all("""
	# 	INSERT INTO "Message" (chat_id, user_id, content, sent) VALUES (%(chat_id)s, %(user_id)s, %(content)s, %(sent)s)
	# 	returning id;
	# 	""",
    #               chat_id=int(chat_id), user_id=int(user_id), content=str(content), sent=sent
    #               )
    #
    # commit()
    # return t


def add_new_file_message(chat_id, user_id, content, sent, filename, type, size):
    m = add_new_message(chat_id, user_id, content, sent)
    print(m)

    mid = m[0]['message_id']
    t = query_all("""
    INSERT INTO "Attachment" (chat_id, user_id, message_id, type, url, size)
    values (%(chat_id)s, %(user_id)s, %(message_id)s, %(type)s, %(filename)s, %(size)s) 
    returning attach_id;
    """,
                  chat_id=int(chat_id),
                  user_id=int(user_id),
                  message_id=int(mid),
                  type=str(type),
                  filename=str(filename),
                  size=int(size)
                  )
    commit()
    return t


def get_messages(chat_id):
    return query_all("""
    SELECT content, "Message".sent, "Message".user_id, "Message".message_id, type, url, size
    FROM "Message" LEFT JOIN "Attachment" ON "Attachment".message_id = "Message".message_id
    WHERE "Message".chat_id = %(chat_id)s
    ORDER BY 4;
    """, chat_id=int(chat_id)
                     )


    # return query_all("""
	# SELECT content, sent, user_id, message_id FROM "Message"
	# WHERE chat_id = %(chat_id)s;
	# """, chat_id=int(chat_id))


def add_new_member_to_chat(user_id, chat_id):
    t = query_all("""
    INSERT INTO "Member" VALUES (%(user_id)s, %(chat_id)s, NULL) RETURNING id;
    """, user_id=int(user_id), chat_id=int(chat_id))
    commit()
    return t


def check_user_existance(user_id):
    return query_all("""
    SELECT * FROM "User"
    WHERE id = %(user_id)s;
    """, user_id=int(user_id))


def create_user(user_id, name, nick):
    t = query_all("""
    INSERT INTO "User" (id, name, nick) VALUES (%(user_id)s, %(name)s, %(nick)s) RETURNING id;
    """,
                  user_id=int(user_id), name=str(name), nick=str(nick))
    commit()
    return t


def get_name_by_id(user_id):
    return query_all("""
    SELECT name FROM "User" WHERE id = %(user_id)s;
    """, user_id=int(user_id))
