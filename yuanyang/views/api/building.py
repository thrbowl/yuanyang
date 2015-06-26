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
def building_list2():
    area_list = Area.query.join(Building).order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    data = {}
    for area in area_list:
        data[area.name] = [building.name for building in area.buildings]

    return jsonify(data)


@building.route('/pro', methods=['GET'])
def building_list1():
    position = request.args['position']
    pn = request.args['pn']
    classify = request.args['classify']
    sort = request.args['sort']
    start = int(request.args['start'])

    area = None
    if position:
        try:
            area = Area.query.filter(Area.name == position).one()
        except:
            return jsonify(message.error(u'该地区不存在'))

    building = None
    if pn:
        try:
            building = Building.query.filter(Building.name == pn).one()
            area = None
        except:
            return jsonify(message.error(u'该楼盘不存在'))

    business_scope = None
    if classify:
        try:
            business_scope = BusinessScope.query.filter(BusinessScope.parent_id != None,
                                                        BusinessScope.name == classify).one()
        except:
            return jsonify(message.error(u'该经营范围不存在'))

    query = Project.query.join(Building)

    if area:
        query = query.filter(Building.area_id == area.id)
    if building:
        query = query.filter(Project.building_id == building.id)
    if business_scope:
        query = query.filter(Project.type_id == business_scope.id)

    if sort == u'发布时间':
        query = query.order_by(Project.publish_date)
    elif sort == u'结束时间':
        query = query.order_by(Project.due_date)

    project_list = query.offset(start).limit(10).all()

    data = [
        {
            'type': project.business_scope.name,
            'imgUrl': project.building.logo,
            'title': project.name,
            'subTitle': project.building.name,
            'state': project.status.get_display_name(),
            'price': project.price_range.get_display_name(),
            'position': project.building.area.name,
            'deadline': convert_to_timestamp(project.due_date),
            'id': project.id
        }
        for project in project_list
    ]
    return json.dumps(data)
