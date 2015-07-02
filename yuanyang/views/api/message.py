# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify, Response
from flask.ext.login import current_user
from ...models import *
from ...message import message as msgutil
from ...utils import login_required

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

    data = [
        {
            'id': msg.id,
            'title': '',
            'content': msg.content,
            'readFlag': msg.is_read,
        }
        for msg in message_list
    ]
    return Response(json.dumps(data), mimetype='application/json')


@message.route('/myMsg/<int:msgId>', methods=['POST'])
@login_required
def read_message(msgId):
    supplier = current_user.supplier

    message = Message.query.get(msgId)
    if message.receiver_id != supplier.id:
        return jsonify(msgutil.error(u'不能读别人的消息'))

    message.read()
    return jsonify(msgutil.ok(u'标记成功'))
