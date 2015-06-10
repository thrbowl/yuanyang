# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect
from flask.ext.login import login_required

entity = Blueprint('admin_entity', __name__)


@entity.route('/add_building', methods=['GET'])
@login_required
def add_building():
    return "PO"
