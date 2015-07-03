# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify
from ...models import Area

area = Blueprint('api_area', __name__)


@area.route('/area_list', methods=['GET'])
def area_list():
    try:
        parent_id = int(request.args['parentId'])
    except:
        parent_id = None

    area_list = Area.query.filter(Area.parent_id == parent_id).all()
    data = dict([(area.id, area.name) for area in area_list])

    return jsonify(data)

