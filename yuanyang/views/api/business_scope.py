# -*- coding: utf-8 -*-
from flask import Blueprint, json, Response
from flask.ext.login import login_required, current_user
from ...models import BusinessScope

business_scope = Blueprint('api_business_scope', __name__)


@business_scope.route('/lv1_scopes', methods=['GET'])
def lv1_scopes():
    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope_list]
    return Response(json.dumps(data), mimetype='application/json')


@business_scope.route('/lv2_scopes', methods=['GET'])
@business_scope.route('/lv2_scopes/<int:business_scope_id>', methods=['GET'])
def lv2_scopes(business_scope_id):
    business_scope = BusinessScope.query.get(business_scope_id)
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope.children]
    return Response(json.dumps(data), mimetype='application/json')


@business_scope.route('/classify', methods=['GET'])
def classify():
    if current_user.is_authenticated():
        business_scope_list = current_user.supplier.business_scopes
    else:
        business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id != None) \
            .order_by(BusinessScope.parent_id.asc(), BusinessScope.order_num.desc(), BusinessScope.create_date.desc()) \
            .all()
    data = [bs.name for bs in business_scope_list]
    return Response(json.dumps(data), mimetype='application/json')
