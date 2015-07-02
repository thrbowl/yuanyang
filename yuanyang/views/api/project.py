# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify, Response
from flask_login import current_user
from ...models import db, catch_db_error, Area, Project, Building, BusinessScope, Bid
from ...message import message
from ...utils import convert_to_timestamp, login_required

project = Blueprint('api_project', __name__)


@project.route('/pro', methods=['GET'])
def project_list():
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
    return Response(json.dumps(data), mimetype='application/json')


@project.route('/pro/<int:project_id>', methods=['GET'])
def project_info(project_id):
    project = Project.query.get(project_id)
    data = {
        'type': project.business_scope.name,
        'imgUrl': project.building.logo,
        'title': project.name,
        'subTitle': project.building.name,
        'state': project.status.get_display_name(),
        'price': project.price_range.get_display_name(),
        'position': project.building.area.name,
        'deadline': convert_to_timestamp(project.due_date),
        'id': project.id,
        'rangeFrom': convert_to_timestamp(project.lead_start_date),
        'rangeTo': convert_to_timestamp(project.lead_end_date),
        'baseInfo': project.requirements,
        'publishTime': convert_to_timestamp(project.publish_date),
    }
    return Response(json.dumps(data), mimetype='application/json')


@project.route('/pro/<int:project_id>', methods=['POST'])
@login_required
@catch_db_error
def bid(project_id):
    company_contact = request.form['contactName']
    company_contact_telephone = request.form['tel']
    email = request.form['mail']
    summary = request.form['desc']

    project = Project.query.get(project_id)
    if not project:
        return jsonify(message.error(u'不存在此项目'))

    supplier = current_user.supplier
    if supplier.is_bid(project_id):
        return jsonify(message.error(u'已经报名过该项目'))

    bid = Bid()
    bid.project_id = project_id
    bid.supplier_id = supplier.id
    bid.company_contact = company_contact
    bid.company_contact_telephone = company_contact_telephone
    bid.email = email
    bid.summary = summary

    db.session.add(bid)
    db.session.commit()

    return jsonify(message.ok(u'报名成功'))
