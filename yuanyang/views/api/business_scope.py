# -*- coding: utf-8 -*-
from flask import Blueprint, json
from flask.ext.login import login_required, redirect
from ...models import BusinessScope

business_scope = Blueprint('api_business_scope', __name__)


@business_scope.route('/lv1_scopes', methods=['GET'])
def lv1_scopes():
    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.id.desc()).all()
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope_list]
    return json.dumps(data)


@business_scope.route('/lv2_scopes', methods=['GET'])
@business_scope.route('/lv2_scopes/<int:business_scope_id>', methods=['GET'])
def lv2_scopes(business_scope_id):
    business_scope = BusinessScope.query.get(business_scope_id)
    data = [{'id': bs.id, 'name': bs.name} for bs in business_scope.children]
    return json.dumps(data)
