# -*- coding: utf-8 -*-
import time
import uuid
from flask import Blueprint, render_template, url_for, request, redirect, g, jsonify, flash, json, current_app
from flask.ext.login import login_required
from flask.ext.uploads import UploadSet, configure_uploads
from ...models import *

entity = Blueprint('admin_entity', __name__)

settings = current_app.config
media = UploadSet(name='media', extensions=settings['UPLOADS_ALLOWED_EXTENSIONS'])
configure_uploads(current_app, media)


@entity.route('/', methods=['GET'])
@login_required('admin')
def index():
    return redirect(url_for('admin_entity.startpage_manage'))


@entity.route('/startpage_manage', methods=['GET'])
@login_required('admin')
def startpage_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    pass


@entity.route('/building_manage', methods=['GET'])
@login_required('admin')
def building_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    pass


@entity.route('/carousel_manage', methods=['GET'])
@login_required('admin')
def carousel_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    pass


@entity.route('/region_manage', methods=['GET'])
@login_required('admin')
def region_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    pass


@entity.route('/set_startpage', methods=['GET'])
@login_required('admin')
def set_startpage():
    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/set_startpage.html')


@entity.route('/add_building', methods=['GET', 'POST'])
@login_required('admin')
def add_building():
    if request.method == 'POST':
        name = request.form['name'].strip()
        region_id = int(request.form['region'])
        owners = request.form.getlist('owners')

        logo_file = request.files['logo']
        logo_folder = time.strftime('%Y%m', time.localtime())
        logo_name = str(uuid.uuid4()) + '.'
        logo_name = media.save(logo_file, folder=logo_folder, name=logo_name)
        full_logo_path = media.url(logo_name)

        building = Building(name)
        building.logo = full_logo_path
        building.region_id = region_id
        for user_id in owners:
            user = User.query.get(user_id)
            building.users.append(user)
        db.session.add(building)

        flash(u'楼盘添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.building_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_building'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    region_list = Region.query.all()
    return render_template('admin/entity/add_building.html', region_list=region_list)


@entity.route('/add_carousel', methods=['GET', 'POST'])
@login_required('admin')
def add_carousel():
    if request.method == 'POST':
        name = request.form['name'].strip()

        image_file = request.files['image']
        image_folder = time.strftime('%Y%m', time.localtime())
        image_name = str(uuid.uuid4()) + '.'
        image_name = media.save(image_file, folder=image_folder, name=image_name)
        full_image_path = media.url(image_name)

        carousel = Carousel(name, full_image_path)
        db.session.add(carousel)

        flash(u'轮播添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.carousel_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_carousel'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/add_carousel.html')


@entity.route('/add_region', methods=['GET', 'POST'])
@login_required('admin')
def add_region():
    if request.method == 'POST':
        name = request.form['name'].strip()

        region = Region(name)
        db.session.add(region)

        flash(u'地区添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.region_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_region'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/add_region.html')


@entity.route('/json/region_users', methods=['GET'])
@entity.route('/json/region_users/<int:region_id>', methods=['GET'])
@login_required('admin')
def region_users(region_id=None):
    data = {}
    if region_id:
        region = Region.query.get(region_id)
        data = dict([(user.id, user.username) for user in region.users])

    return jsonify(data)


@entity.route('/json/check_region_unique', methods=['GET'])
@login_required('admin')
def check_region_unique():
    name = request.args['name'].strip()
    is_unique = (Region.query.filter(Region.name == name).count() == 0)

    return json.dumps(is_unique)


@entity.route('/json/check_building_unique', methods=['GET'])
@login_required('admin')
def check_building_unique():
    name = request.args['name'].strip()
    is_unique = (Building.query.filter(Building.name == name).count() == 0)

    return json.dumps(is_unique)
