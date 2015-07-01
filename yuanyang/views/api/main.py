# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify, Response
from flask.ext.login import login_user, logout_user
from ...models import db, catch_db_error, Carousel
from ...message import OK_MESSAGE, ERROR_MESSAGE
from ...utils import login_required

main = Blueprint('api_main', __name__)


@main.route('/carousel', methods=['GET'])
def carousel_list():
    carousel_list1 = Carousel.query.order_by(Carousel.order_num.desc()).all()
    data = {
        'data': [{'title': carousel.name, 'imgUrl': carousel.image} for carousel in carousel_list1]
    }
    return Response(json.dumps(data), mimetype='application/json')
