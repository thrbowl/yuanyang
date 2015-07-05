# -*- coding: utf-8 -*-
from flask import Blueprint
from flask.ext.login import current_user
from ...models import *
from ...utils import jsonify

business_scope = Blueprint('api_business_scope', __name__)


@business_scope.route('/lv1_scopes', methods=['GET'])
def lv1_scopes():
    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope_list]
    return jsonify(data)

@business_scope.route('/lv2_scopes', methods=['GET'])
@business_scope.route('/lv2_scopes/<int:business_scope_id>', methods=['GET'])
def lv2_scopes(business_scope_id):
    business_scope = BusinessScope.query.get(business_scope_id)
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope.children]
    return jsonify(data)


@business_scope.route('/classify', methods=['GET'])
def classify():
    if current_user.is_authenticated():
        supplier = current_user.supplier
        business_scope_list = supplier.business_scopes
    else:
        business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id != None) \
            .order_by(BusinessScope.parent_id.asc(), BusinessScope.order_num.desc(), BusinessScope.create_date.desc()) \
            .all()
    data = [bs.name for bs in business_scope_list]
    return jsonify(data)
