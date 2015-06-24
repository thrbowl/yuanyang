# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify
from ...models import Area, User

user = Blueprint('api_user', __name__)


@user.route('/user_list', methods=['GET'])
def user_list():
    try:
        area_id = int(request.args['area_id'])

        area = Area.query.get(area_id)
        user_list = area.users
    except:
        user_list = User.query.all()

    data = [{'id': user.id, 'name': user.username} for user in user_list]

    return json.dumps(data)
