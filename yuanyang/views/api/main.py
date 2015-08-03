# -*- coding: utf-8 -*-
import os
from flask import Blueprint, request, send_file
from flask.ext.login import current_user
from ...message import message
from ...models import *
from ...utils import convert_to_timestamp, jsonify, login_required, remove_if_startwith

main = Blueprint('api_main', __name__)

settings = current_app.config

@main.route('/enter.jpg', methods=['GET'])
def first_img():
    startpage = StartPage.query.filter(StartPage.is_active == True).one()
    img_path = os.path.join(settings['STATIC_BASE_ROOT'], remove_if_startwith(startpage.image, '/static/'))
    return send_file(img_path, mimetype='image/jpeg')


@main.route('/carousel', methods=['GET'])
def carousel_list():
    carousel_list1 = Carousel.query.order_by(Carousel.order_num.desc()).all()
    data = {
        'data': [{'title': carousel.name, 'imgUrl': carousel.image} for carousel in carousel_list1]
    }
    return jsonify(data)


@main.route('/province', methods=['GET'])
def province_list():
    area_list = Area.query.filter(Area.parent_id == None)\
        .order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    data = [{'id': area.id, 'name': area.name} for area in area_list]
    return jsonify(data)


@main.route('/city', methods=['GET'])
def city_list():
    province_id = int(request.args['province_id'])
    area_list = Area.query.filter(Area.parent_id == province_id)\
        .order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    if not area_list:
        area = Area.query.get(province_id)
        area_list = [area]
    data = [{'id': area.id, 'name': area.name} for area in area_list]
    return jsonify(data)


@main.route('/me', methods=['GET'])
@login_required
def my_info():
    supplier = current_user.supplier

    winCount = Project.query.filter(Project.supplier_id==supplier.id).count()
    data = {
        'imgUrl': '',
        'companyName': supplier.company_name,
        'mail': supplier.email,
        'authenticated': supplier.status,
        'mark': supplier.service_score,
        'bidCount': len(supplier.bids),
        'winCount': winCount,
        'id': supplier.id,
    }
    return jsonify(data)


@main.route('/comment', methods=['GET'])
@login_required
def my_comment():
    supplier = current_user.supplier

    comment_list = supplier.comments
    data = [
        {
            'id': comment.id,
            'readFlag': comment.is_read,
            'title': '',
            'content': comment.content,
            'mark': comment.service_score,
            'commentNum': 0
        }
        for comment in comment_list
    ]
    return jsonify(data)


@main.route('/comment/<int:comment_id>', methods=['GET'])
def comment_info(comment_id):
    comment = Comment.query.get(comment_id)

    data = {
        'title': '',
        'content': comment.content,
        'serviceMark': comment.service_score,
        'costMark': comment.cost_score,
        'quantityMark': comment.quality_score,
        'timeMark': comment.time_score,
        'comments': [],
    }
    return jsonify(data)


@main.route('/comment/<int:comment_id>', methods=['POST'])
@catch_db_error
@login_required
def comment_appeal(comment_id):
    appeal = request.form['content']

    comment = Comment.query.get(comment_id)
    comment.appeal = appeal
    db.session.commit()

    return jsonify(message.ok(u'申诉提交成功'))


@main.route('/bid', methods=['GET'])
@login_required
def bid_list():
    type = request.args['type'].strip()
    start = int(request.args['start'])

    supplier = current_user.supplier

    if type == 'bid':
        bid_list1 = Bid.query.filter(Bid.supplier_id == supplier.id).order_by(Bid.create_date.desc()) \
            .offset(start).limit(10).all()
    elif type == 'win':
        bid_list1 = Bid.query.join(Project).filter(Bid.supplier_id == supplier.id, Bid.id == Project.bid_id) \
            .order_by(Bid.create_date.desc()).offset(start).limit(10).all()
    else:
        return jsonify(message.error(u'类型不正确'))

    data = []
    for bid in bid_list1:
        project = bid.project
        data.append(
            {
                'type': project.business_scope.name,
                'imgUrl': project.building.logo,
                'title': project.name,
                'subTitle': project.building.name,
                'state': project.status.get_display_name(),
                'from': convert_to_timestamp(project.lead_start_date),
                'to': convert_to_timestamp(project.lead_end_date),
                'publishTime': convert_to_timestamp(project.publish_date),
                'deadline': convert_to_timestamp(project.due_date),
                'id': project.id,
                'price': project.price_range.get_display_name(),
            }
        )
    return jsonify(data)


@main.route('/enterInfoValidated', methods=['GET'])
@login_required
def check_supplier_status():
    supplier = current_user.supplier

    result = supplier.status == Supplier.STATUS_PASS
    return jsonify(result)


@main.route('/project_supplier', methods=['GET'])
def project_supplier():
    project_id = int(request.args['project_id'])

    project = Project.query.get(project_id)
    if not project:
        return jsonify(message.error(u'项目不存在'))

    if not project.supplier_id:
        return jsonify(message.error(u'供应商不存在'))

    supplier = Supplier.query.get(project.supplier_id)
    data = {
        'companyName': supplier.company_name,
        'contactName': supplier.company_contact,
        'tel': supplier.company_contact_telephone,
        'position': supplier.area and supplier.area.full_name,
        'addrSpec': supplier.company_address,
        'bank': supplier.deposit_bank,
        'account': supplier.bank_account,
    }
    return jsonify(data)
