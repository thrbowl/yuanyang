# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect
from flask.ext.login import login_required

user = Blueprint('admin_user', __name__)


@user.route('/', methods=['GET'])
@login_required
def index():
    return "PO"
