# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect
from flask.ext.login import login_required, current_user
from flask.ext.login import login_required

main = Blueprint('admin_main', __name__)


@main.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('admin_project.index'))
