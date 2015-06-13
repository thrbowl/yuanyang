# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, current_app, redirect, g
from flask.ext.login import login_required, current_user
from ...models import *

user = Blueprint('admin_user', __name__)


@user.route('/', methods=['GET'])
@login_required('admin')
def index():
    return redirect(url_for('admin_user.user_list'))


@user.route('/user_list', methods=['GET'])
@login_required('admin')
def user_list():
    g.breadcrumbs = [u'用户管理', u'用户列表']
    g.menu = 'user'

    user_list = User.query.filter(User.is_superuser != True).order_by(User.id.desc()).all()
    return render_template('admin/user/user_list.html', user_list=user_list)


@user.route('/add_user', methods=['GET'])
@login_required('admin')
def add_user():
    g.breadcrumbs = [u'用户管理', u'添加新用户']
    g.menu = 'user'

    region_list =Region.query.all()
    return render_template('admin/user/add_user.html', region_list=region_list)


@user.route('/update_user', methods=['GET'])
@login_required('admin')
def update_user():
    g.breadcrumbs = [u'用户管理', u'编辑用户']
    g.menu = 'user'

    return render_template('admin/user/update_user.html')
