# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect
from flask.ext.login import login_required, current_user

supplier = Blueprint('admin_supplier', __name__)


@supplier.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('admin_supplier.supplier_list'))


@supplier.route('/supplier_list', methods=['GET'])
@login_required
def supplier_list():
    pass
