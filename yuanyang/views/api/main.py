# -*- coding: utf-8 -*-
import os
from flask import Blueprint, request, send_file
from flask.ext.login import current_user
from ...models import *
from ...utils import jsonify, login_required, remove_if_startwith

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
        'authenticated': supplier.status == Supplier.STATUS_PASS,
        'mark': supplier.service_score,
        'bidCount': len(supplier.bids),
        'winCount': winCount,
        'id': supplier.id,
    }
    return jsonify(data)
