# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify
from ...models import Area, Building

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
