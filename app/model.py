from .db import *
from app import app

def get_user():
    return query_one("""
    SELECT * FROM "User";
    """)


def get_users_list_by_mask(mask):
    return query_all("""
        SELECT * FROM "User"
        WHERE "name" LIKE %(mask)s;
    """, mask=str(mask))


def get_chats_list():
    return query_all("""
		SELECT * FROM "Chat";
	""")


def get_members_list(user_id):
    return query_all("""
		SELECT topic, "Chat".chat_id FROM "Chat"
		JOIN "Member" ON "Chat".chat_id = "Member".chat_id
		AND user_id = %(user_id)s;
	""",
                     user_id=user_id)


def add_new_chat(is_group_chat, topic):
    t = query_all("""
		INSERT INTO "Chat" (is_group_chat, topic, last_message) VALUES (%(is_group_chat)s, %(topic)s, NULL)
		RETURNING chat_id;
	""",
                  is_group_chat=str(is_group_chat),
                  topic=str(topic))
    commit()
    return t


def add_new_message(chat_id, user_id, content, sent):
    t = query_all("""
		INSERT INTO "Message" (chat_id, user_id, content, sent) VALUES (%(chat_id)s, %(user_id)s, %(content)s, %(sent)s)
		returning message_id;
		""",
                  chat_id=int(chat_id), user_id=int(user_id), content=str(content), sent=sent
                  )

    commit()
    return t


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
    INSERT INTO "Member" VALUES (%(user_id)s, %(chat_id)s, NULL) RETURNING member_id;
    """, user_id=int(user_id), chat_id=int(chat_id))
    commit()
    return t


def check_user_existance(user_id):
    return query_all("""
    SELECT * FROM "User"
    WHERE user_id = %(user_id)s;
    """, user_id=int(user_id))


def create_user(user_id, name, nick):
    t = query_all("""
    INSERT INTO "User" (user_id, name, nick) VALUES (%(user_id)s, %(name)s, %(nick)s) RETURNING user_id;
    """,
                  user_id=int(user_id), name=str(name), nick=str(nick))
    commit()
    return t


def get_name_by_id(user_id):
    return query_all("""
    SELECT name FROM "User" WHERE user_id = %(user_id)s;
    """, user_id=int(user_id))
