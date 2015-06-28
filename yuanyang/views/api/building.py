# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify
from ...models import Area, Building, BusinessScope, Project
from ...message import message
from ...utils import convert_to_timestamp

building = Blueprint('api_building', __name__)


@building.route('/building_list', methods=['GET'])
def building_list():
    try:
        area_id = int(request.args['area_id'])

        area = Area.query.get(area_id)
        building_list = area.buildings
    except:
        building_list = Building.query.all()

    data = [{'id': building.id, 'name': building.name} for building in building_list]

    return json.dumps(data)


@building.route('/pnList', methods=['GET'])
def building_list1():
    area_list = Area.query.join(Building).order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    data = {}
    for area in area_list:
        data[area.name] = [building.name for building in area.buildings]

    return jsonify(data)
