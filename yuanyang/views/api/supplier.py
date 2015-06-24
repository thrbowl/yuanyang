# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, request, session, json, jsonify
from flask.ext.login import login_required, redirect
from ...models import Supplier

supplier = Blueprint('api_supplier', __name__)


@supplier.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']


@supplier.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    supplie = Supplier.get(username)
    if not supplier:
        return
    elif supplier:
        pass

    session['supplier_id'] = supplie.id


@supplier.route('/logout', methods=['POST'])
@login_required
def logout():
    pass

