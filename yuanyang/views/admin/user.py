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
    g.breadcrumbs = [
        (u'用户管理', url_for('admin_user.index')),
        (u'用户列表', '#')
    ]
    g.menu = 'user'

    page = int(request.args.get('page', 1))
    per_page = 10
    pager = User.query.filter(User.is_backend == True, User.is_superuser != True).order_by(User.create_date.desc()) \
        .paginate(page, per_page, False)
    return render_template('admin/user/user_list.html', pager=pager)


@user.route('/add_user', methods=['GET', 'POST'])
@login_required('admin')
def add_user():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        area_id = int(request.form['area_id'])
        buildings = request.form.getlist('buildings')

        user = User(username, password)
        user.area_id = area_id
        user.buildings = [Building.query.get(building_id) for building_id in buildings]
        user.is_backend = True
        db.session.add(user)
        db.session.commit()

        flash(u'添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_user.user_list'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_user.add_user'))

    g.breadcrumbs = [
        (u'用户管理', url_for('admin_user.index')),
        (u'添加用户', '#')
    ]
    g.menu = 'user'
    return render_template('admin/user/add_user.html')


@user.route('/edit_user', methods=['GET', 'POST'])
@user.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        password = request.form['password'].strip()
        area_id = int(request.form['area_id'])
        buildings = request.form.getlist('buildings')

        user.password = password
        user.area_id = area_id
        user.buildings = [Building.query.get(building_id) for building_id in buildings]
        db.session.commit()

        flash(u'更新成功')
        return redirect(url_for('admin_user.user_list'))

    g.breadcrumbs = [
       (u'用户管理', url_for('admin_user.index')),
       (u'编辑用户', '#')
    ]
    g.menu = 'user'
    return render_template('admin/user/edit_user.html', user=user)


@user.route('/json/delete_user', methods=['POST'])
@login_required('admin')
def delete_user():
    user_id = int(request.form['user_id'])

    user1 = User.query.get(user_id)
    db.session.delete(user1)
    db.session.commit()

    flash(u'删除成功')
    return jsonify(SUCCESS_MESSAGE)


########################################################################################################################
@user.route('/json/check_user_unique', methods=['GET'])
@login_required('admin')
def check_user_unique():
    username = request.args['username'].strip()
    prev_username = request.args.get('prev_username')

    is_unique = (prev_username == username)
    if not is_unique:
        is_unique = (User.query.filter(User.username == username).count() == 0)

    return json.dumps(is_unique)


@login_required('admin')
@user.route('/json/area_users', methods=['GET'])
def area_users():
    try:
        area_id = int(request.args['area_id'])

        area = Area.query.get(area_id)
        user_list = area.users
    except:
        user_list = User.query.filter(User.is_backend == True, User.is_superuser != True) \
            .order_by(User.create_date.desc()).all()

    data = [{'id': user.id, 'name': user.username} for user in user_list]

    return json.dumps(data)
