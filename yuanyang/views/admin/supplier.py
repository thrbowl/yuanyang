# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect
from flask.ext.login import login_required

supplier = Blueprint('admin_supplier', __name__)


@supplier.route('/', methods=['GET'])
@login_required
def index():
    return "PO"
