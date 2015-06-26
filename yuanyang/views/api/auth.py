# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify
from flask.ext.login import login_user, logout_user
from ...models import db, User, Supplier, catch_db_error
from ...message import message
from ...utils import login_required

auth = Blueprint('api_auth', __name__)


@auth.route('/reg', methods=['POST'])
@catch_db_error
def register():
    username = request.form['user'].strip()
    password = request.form['passwd'].strip()
    mail = request.form['mail'].strip()

    user = User(username, password)
    db.session.add(user)
    supplier = Supplier(user, mail)
    db.session.add(supplier)
    db.session.commit()

    return jsonify(message.ok(u'注册成功'))


@auth.route('/check_user_unique', methods=['GET'])
def check_user_unique():
    username = request.args['user'].strip()
    prev_username = request.args.get('prev_user')

    is_unique = (prev_username == username)
    if not is_unique:
        is_unique = (User.query.filter(User.username == username).count() == 0)

    return json.dumps(is_unique)


@auth.route('/login', methods=['POST'])
def login():
    username = request.form['user'].strip()
    password = request.form['passwd'].strip()

    user = User.get(username)
    if not user:
        return jsonify(message.ok(u'用户不存在'))
    elif user.password != password:
        return jsonify(message.ok(u'用户名与密码不匹配'))

    login_user(user)
    return jsonify(message.ok(u'登录成功'))


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify(message.ok(u'退出成功'))
