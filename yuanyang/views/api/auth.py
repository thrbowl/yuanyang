# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask.ext.login import current_user, login_user, logout_user
from ...models import *
from ...message import message
from ...utils import jsonify, login_required, send_email

auth = Blueprint('api_auth', __name__)


@auth.route('/reg', methods=['POST'])
@catch_db_error
def register():
    username = request.form['user'].strip()
    password = request.form['passwd'].strip()
    mail = request.form['mail'].strip()

    is_unique = (User.query.filter(User.username == username).count() == 0)
    if not is_unique:
        return jsonify(message.error(u'该用户已经存在'))

    is_unique = (Supplier.query.filter(Supplier.email == mail).count() == 0)
    if not is_unique:
        return jsonify(message.error(u'该邮箱已经被使用'))

    user = User(username, password)
    db.session.add(user)
    supplier = Supplier(user, mail)
    db.session.add(supplier)
    db.session.commit()

    login_user(user)

    return jsonify(message.ok(u'注册成功'))


@auth.route('/check_user_unique', methods=['GET'])
def check_user_unique():
    username = request.args['user'].strip()
    prev_username = request.args.get('prev_user')

    is_unique = (prev_username == username)
    if not is_unique:
        is_unique = (User.query.filter(User.username == username).count() == 0)

    return jsonify(is_unique)


@auth.route('/login', methods=['POST'])
def login():
    username = request.form['user'].strip()
    password = request.form['passwd'].strip()

    user = User.get(username)
    if not user:
        return jsonify(message.error(u'用户不存在'))
    elif user.password != password:
        return jsonify(message.error(u'用户名与密码不匹配'))

    login_user(user)
    return jsonify(message.ok(u'登录成功'))


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify(message.ok(u'退出成功'))


@auth.route('/forget', methods=['POST'])
def forget_pwd():
    username = request.form['user'].strip()
    mail = request.form['mail'].strip()

    try:
        user = User.query.filter(User.username == username).one()
        if user.supplier.email == mail:
            send_email(u'找回密码', u'您的密码是：%s，请妥善保管。', mail)
            return jsonify(message.ok(u'密码发送成功'))
        else:
            return jsonify(message.ok(u'用户和邮箱不匹配'))
    except:
        return jsonify(message.ok(u'用户不存在'))


@auth.route('/checkLogin', methods=['GET'])
def check_login():
    return jsonify(current_user.is_authenticated())
