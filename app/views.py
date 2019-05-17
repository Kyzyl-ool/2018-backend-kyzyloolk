from flask import request, abort, jsonify, redirect
from app import app, jsonrpc, s3_client, cent_client
from .model import *
from .vk_requests import *
from .checkers import *
from .tasks import *
from .emails import *

import json
import time
import requests
import base64
import jwt
import config

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper

from pymemcache.client import base

memcache_client = base.Client(('127.0.0.1', 11211))

emojis_amount = {
    'activity': 107
}

from os import walk

emoji_names = []
for (dirpath, dirnames, filenames) in walk('/www/meowbook.ru/backend/public/activity'):
    emoji_names.extend(filenames)
    break

emoji_names.sort()


@jsonrpc.method('new_chat')
def new_chat(topic, is_group):
    if (
            not isNone(topic) and not isNone(is_group) and
            isString(topic) and isString(is_group)
    ):
        send_mail.delay('TEST', 'kyzylool.km@gmail.com', ['kyzyl.okm@phystech.edu'], "SOME_CONTENT", '<b>123</b>')
        return jsonify(add_new_chat(is_group, topic)).json
    else:
        return {'code': 400}


@jsonrpc.method('new_message')
def new_message(chat_id, user_id, content, time):
    # print(chat_id, user_id, content, sep='\n')
    # publish data into channel

    # channel = "public:chat1"
    # data = {"text": content}
    # cent_client.publish(channel, data)

    # the_time = time.strftime('%Y-%m-%d %H:%M:%S')
    the_time = time

    cent_client.broadcast([str(chat_id)], {
        'user_id': user_id,
        'content': content,
        'time': the_time,
        'spanText': '',
        'id': chat_id
    })

    print('NEW MESSAGE')

    if (
            not isNone(chat_id) and not isNone(user_id) and not isNone(content) and
            isInt(chat_id) and isInt(user_id) and isString(content)
    ):
        memcache_client.delete('get_messages({})'.format(chat_id))
        return add_new_message(chat_id, user_id, content, the_time)
    else:
        return {'code': 400}


@jsonrpc.method('new_file_message')
def new_file_message(chat_id, user_id, content, filename, type, size, time):
    if (
            not isNone(chat_id) and not isNone(user_id) and not isNone(content) and not isNone(filename) and not isNone(
        type) and not isNone(size) and
            isInt(chat_id) and isInt(user_id) and isString(content) and isString(filename) and isString(type) and isInt(
        size)
    ):
        memcache_client.delete('get_messages({})'.format(chat_id))
        print('NEW FILE MESSAGE')

        # the_time = time.strftime('%Y-%m-%d %H:%M:%S')
        the_time = time
        cent_client.broadcast([str(chat_id)], {
            'user_id': user_id,
            'content': content,
            'time': the_time,
            'spanText': '',
            'id': chat_id,
            'filename': filename,
            'filetype': type,
            'filesize': size
        })

        return add_new_file_message(chat_id, user_id, content, the_time, filename, type, size)
    else:
        return {'code': 400}


@jsonrpc.method('get_users')
def get_users(mask):
    if (not isNone(mask) and isString(mask)):
        return jsonify(get_users_list_by_mask(mask)).json
    else:
        return {'code': 400}


@jsonrpc.method('get_chats')
def get_chats(user_id):
    return jsonify(get_members_list(user_id)).json


@jsonrpc.method('get_messages')
def get_message(chat_id):
    if (not isNone(chat_id) and
            isInt(chat_id)
    ):
        result = memcache_client.get('get_messages({})'.format(chat_id))
        if result is None:
            # print('messages of chat {} taken from DB'.format(chat_id))
            result = jsonify(get_messages(chat_id)).json
            memcache_client.set('get_messages({})'.format(chat_id), json.dumps(result))
        else:
            # print('messages of chat {} from memcache'.format(chat_id))
            result = json.loads(result)

        return result
    else:
        return {'code': 400}


@app.route('/backend/get_first_token/')
def get_first_token_method():
    return get_first_token()


@jsonrpc.method('get_access_token')
def get_access_token_method(code):
    return get_access_token(code)


# json_data = json.loads(resp.text)
# return json_data

@jsonrpc.method('get_user_data')
def get_user_data_method(access_token, user_id):
    return get_user_data(access_token, user_id)


@jsonrpc.method('upload_file')
def upload_file(base64content, filename):
    # print('b64: ', base64content)
    # print('filename: ', filename)
    if (s3_client.put_object(
            Bucket=config.BUCKET_NAME,
            Key=filename,
            Body=base64.b64decode(base64content))):
        s3_client.download_file(Bucket=config.BUCKET_NAME, Key=filename,
                                Filename='/www/meowbook.ru/backend/public/' + filename)
        memcache_client.set('file_' + filename, 1)
        return {'code': 200}
    else:
        return {'code': 500, 'error': 'Error with s3 client.'}


@jsonrpc.method('download_file')
def download_file(filename, filetype):
    # file_flag = memcache_client.get('file_'+filename)
    # if file_flag is None:
    # s3_client.download_file(Bucket=config.BUCKET_NAME, Key=filename, Filename='/www/meowbook.org/public/'+filename)
    #     memcache_client.set('file_'+filename, 1)
    #     return {'code': 200, 'text': 'file '+filename+' downloaded', 'name': filename, 'type': filetype}

    # return {'code': 200, 'text': 'file '+filename+' taken from server', 'name': filename, 'type': filetype}

    the_object = s3_client.get_object(Bucket=config.BUCKET_NAME, Key=filename)
    bytes = the_object['Body'].read()
    encoded_bytes = base64.b64encode(bytes).decode('utf-8')
    return {'file': encoded_bytes, 'type': filetype, 'name': filename, 'lastmodified': the_object['LastModified']}


from time import sleep


@jsonrpc.method('get_centrifuge_token')
def get_centrifuge_token(user_id):
    return jwt.encode({"sub": "0"}, config.CENTRIFUGO_SECRET).decode()


@jsonrpc.method('add_new_member_to_chat')
def add_new_member_to_chat_method(user_id, chat_id):
    if (not isNone(user_id) and not isNone(chat_id) and
            isInt(user_id) and isInt(chat_id)):
        return add_new_member_to_chat(user_id, chat_id)
    else:
        return {'code': 400}


@jsonrpc.method('check_user')
def check_user_method(user_id):
    if (not isNone(user_id) and isInt(user_id)):
        return jsonify(check_user_existance(user_id)).json
    else:
        return {'code': 400}


@jsonrpc.method('create_user')
def create_user_method(user_id, name, nick):
    if (not isNone(user_id) and isInt(user_id) and
            not isNone(name) and isString(name) and
            not isNone(nick) and isString(nick) and
            user_id > 0):
        return create_user(user_id, name, nick)
    else:
        return {'code': 400}


@jsonrpc.method('user_name_by_id')
def user_name_by_id_method(user_id):
    if (not isNone(user_id) and isInt(user_id)):
        return get_name_by_id(user_id)
    else:
        return {'code': 400}


@jsonrpc.method('get_emojis_amount')
def get_emojis_amount(emojis):
    if isString(emojis):
        return emojis_amount[emojis]
    else:
        return {'code': 400}


@jsonrpc.method('get_emoji_name')
def get_emoji_name(emoji_id):
    if isInt(emoji_id):
        return emoji_names[emoji_id]
    else:
        return {'code': 400}


@jsonrpc.method('get_emoji_file')
def get_emoji_file(emoji_id):
    if isInt(emoji_id):
        with open('/www/meowbook.ru/backend/public/activity/128/' + emoji_names[emoji_id], "rb") as image_file:
            return {'file': base64.b64encode(image_file.read()).decode('utf-8'), 'name': emoji_names[emoji_id]}
    else:
        return {'code': 400}


@jsonrpc.method('run_task')
def method_run_task(text):
    run_main_task(text)
    return {'code': 200, 'text': text}
