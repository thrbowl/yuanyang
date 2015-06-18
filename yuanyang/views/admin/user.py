# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, g, request, jsonify, json, flash
from flask.ext.login import login_required
from ...models import *
from ...message import SUCCESS_MESSAGE, ERROR_MESSAGE

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

    page = int(request.args.get('page', 1))
    per_page = 10
    pager = User.query.filter(User.is_superuser != True).order_by(User.id.desc()).paginate(page, per_page, False)
    return render_template('admin/user/user_list.html', pager=pager)


@user.route('/add_user', methods=['GET', 'POST'])
@login_required('admin')
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        region_id = int(request.form['region'])
        buildings = request.form.getlist('buildings')

        user = User(username, password)
        user.region_id = region_id
        user.buildings = [Building.query.get(building_id) for building_id in buildings]
        db.session.add(user)
        db.session.commit()

        flash(u'用户添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_user.user_list'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_user.add_user'))

    g.breadcrumbs = [u'用户管理', u'添加新用户']
    g.menu = 'user'
    region_list = Region.query.all()
    return render_template('admin/user/add_user.html', region_list=region_list)


@user.route('/edit_user', methods=['GET', 'POST'])
@user.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        password = request.form['password'].strip()
        region_id = int(request.form['region'])
        buildings = request.form.getlist('buildings')

        user.password = password
        user.region_id = region_id
        user.buildings = [Building.query.get(building_id) for building_id in buildings]
        db.session.commit()

        flash(u'用户更新成功')
        return redirect(url_for('admin_user.user_list'))

    g.breadcrumbs = [u'用户管理', u'编辑用户']
    g.menu = 'user'
    region_list = Region.query.all()
    return render_template('admin/user/edit_user.html', user=user, region_list=region_list)


@user.route('/json/delete_user', methods=['POST'])
@login_required('admin')
def delete_user():
    user_id = int(request.form['user_id'])

    user1 = User.query.get(user_id)
    db.session.delete(user1)
    db.session.commit()
    flash(u'用户删除成功')

    return jsonify(SUCCESS_MESSAGE)


########################################################################################################################
@user.route('/json/region_buildings', methods=['GET'])
@user.route('/json/region_buildings/<int:region_id>', methods=['GET'])
@login_required('admin')
def region_buildings(region_id):
    region = Region.query.get(region_id)
    data = dict([(building.id, building.name) for building in region.buildings])

    return jsonify(data)


@user.route('/json/check_user_unique', methods=['GET'])
@login_required('admin')
def check_user_unique():
    username = request.args['username'].strip()
    prev_username = request.args.get('prev_username')

    is_unique = (prev_username == username)
    if not is_unique:
        is_unique = (User.query.filter(User.username == username).count() == 0)

    return json.dumps(is_unique)
