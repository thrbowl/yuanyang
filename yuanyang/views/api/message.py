# -*- coding: utf-8 -*-
import json
from flask import Blueprint, request
from flask.ext.login import current_user
from ...message import message as msgutil
from ...models import *
from ...utils import convert_to_timestamp, jsonify, login_required

message = Blueprint('api_message', __name__)


@message.route('/myMsg', methods=['GET'])
@login_required
def message_list():
    type = request.args['type']
    start = int(request.args['start'])

    supplier = current_user.supplier

    if type == 'pro':
        type = Message.TYPE_PROJECT
    elif type == 'sys':
        type = Message.TYPE_SYSTEM
    else:
        return jsonify(msgutil.error(u'类型不正确'))

    message_list = Message.query.filter(Message._type == type, Message.receiver_id == supplier.id) \
        .offset(start).limit(10).all()

    data = []
    for msg in message_list:
        d = {
            'id': msg.id,
            'type': msg.title,
            'title': msg.title.get_display_name(),
            'content': msg.content,
            'readFlag': msg.is_read,
            'time': convert_to_timestamp(msg.create_date)
        }
        d.update(json.loads(msg.data))
        data.append(d)

    return jsonify(data)


@message.route('/myMsg/<int:msgId>', methods=['POST'])
@login_required
@catch_db_error
def read_message(msgId):
    supplier = current_user.supplier

    message = Message.query.get(msgId)
    if message.receiver_id != supplier.id:
        return jsonify(msgutil.error(u'不能读别人的消息'))

    message.read()
    db.session.commit()

    return jsonify(msgutil.ok(u'标记成功'))
