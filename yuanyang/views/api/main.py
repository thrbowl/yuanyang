# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask.json import dumps
from ...models import db, catch_db_error, Carousel, Area
from ...message import message, OK_MESSAGE, ERROR_MESSAGE
from ...utils import login_required, jsonify

main = Blueprint('api_main', __name__)


@main.route('/carousel', methods=['GET'])
def carousel_list():
    carousel_list1 = Carousel.query.order_by(Carousel.order_num.desc()).all()
    data = {
        'data': [{'title': carousel.name, 'imgUrl': carousel.image} for carousel in carousel_list1]
    }
    return jsonify(data)


@main.route('/province', methods=['GET'])
def province_list():
    province_list1 = Area.query.filter(Area.parent == None)\
        .order_by(Area.order_num.desc(), Area.create_date.desc).all()
    data = [province.name for province in province_list1]


@main.route('/city', methods=['GET'])
def city_list():
    province = request.args['province']
