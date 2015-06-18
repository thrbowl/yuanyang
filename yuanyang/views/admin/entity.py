# -*- coding: utf-8 -*-
import time
import uuid
from flask import Blueprint, render_template, url_for, request, redirect, g, jsonify, flash, json, current_app
from flask.ext.login import login_required
from flask.ext.uploads import UploadSet, configure_uploads
from ...models import *
from ...utils import check_image_size
from ...message import SUCCESS_MESSAGE, ERROR_MESSAGE

entity = Blueprint('admin_entity', __name__)

settings = current_app.config
media = UploadSet(name='media', extensions=settings['UPLOADS_ALLOWED_EXTENSIONS'])
configure_uploads(current_app, media)


@entity.route('/', methods=['GET'])
@login_required('admin')
def index():
    return redirect(url_for('admin_entity.building_manage'))


########################################################################################################################
@entity.route('/startpage_manage', methods=['GET'])
@login_required('admin')
def startpage_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    pass


@entity.route('/add_startpage', methods=['GET'])
@login_required('admin')
def add_startpage():
    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/add_startpage.html')


########################################################################################################################
@entity.route('/building_manage', methods=['GET'])
@login_required('admin')
def building_manage():
    g.breadcrumbs = [u'信息管理', u'楼盘管理']
    g.menu = 'entity'

    page = int(request.args.get('page', 1))
    per_page = 10
    pager = Building.query.order_by(Building.order_num.desc(), Building.id.desc()).paginate(page, per_page, False)
    return render_template('admin/entity/building_list.html', pager=pager)


@entity.route('/add_building', methods=['GET', 'POST'])
@login_required('admin')
def add_building():
    if request.method == 'POST':
        name = request.form['name'].strip()
        region_id = int(request.form['region'])
        owners = request.form.getlist('owners')

        logo_file = request.files['logo']
        full_logo_url = ''
        if logo_file.name:
            logo_folder = time.strftime('%Y%m', time.localtime())
            logo_name = str(uuid.uuid4()) + '.'
            logo_name = media.save(logo_file, folder=logo_folder, name=logo_name)
            full_logo_url = media.url(logo_name)
            full_logo_root = media.path(logo_name)
            if not check_image_size(full_logo_root, *settings['BUILDING_LOGO_SIZE']):
                flash(u'添加失败，图片尺寸必须为%s' % str(settings['BUILDING_LOGO_SIZE']))
                return redirect(url_for('admin_entity.add_building'))

        building = Building(name)
        building.logo = full_logo_url
        building.region_id = region_id
        building.users = [User.query.get(user_id) for user_id in owners]
        db.session.add(building)
        db.session.commit()

        flash(u'楼盘添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.building_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_building'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    region_list = Region.query.all()
    return render_template('admin/entity/add_building.html', region_list=region_list)


@entity.route('/edit_building', methods=['GET', 'POST'])
@entity.route('/edit_building/<int:building_id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_building(building_id):
    building = Building.query.get(building_id)
    if request.method == 'POST':
        name = request.form['name'].strip()
        region_id = int(request.form['region'])
        owners = request.form.getlist('owners')

        building.name = name
        building.region_id = region_id
        building.users = [User.query.get(user_id) for user_id in owners]

        logo_file = request.files['logo']
        if logo_file.filename:
            logo_folder = time.strftime('%Y%m', time.localtime())
            logo_name = str(uuid.uuid4()) + '.'
            logo_name = media.save(logo_file, folder=logo_folder, name=logo_name)
            full_logo_url = media.url(logo_name)
            full_logo_root = media.path(logo_name)
            if not check_image_size(full_logo_root, *settings['BUILDING_LOGO_SIZE']):
                flash(u'更新失败，图片尺寸必须为%s' % str(settings['BUILDING_LOGO_SIZE']))
                return redirect(url_for('admin_entity.edit_building'))
            building.logo = full_logo_url
        db.session.commit()

        flash(u'楼盘更新成功')
        return redirect(url_for('admin_entity.building_manage'))

    g.breadcrumbs = [u'信息管理', u'编辑信息']
    g.menu = 'entity'
    region_list = Region.query.all()
    return render_template('admin/entity/edit_building.html', building=building, region_list=region_list)


@entity.route('/json/delete_building', methods=['POST'])
@login_required('admin')
def delete_building():
    building_id = int(request.form['building_id'])

    building = Building.query.get(building_id)
    db.session.delete(building)
    db.session.commit()
    flash(u'楼盘删除成功')

    return jsonify(SUCCESS_MESSAGE)


########################################################################################################################
@entity.route('/carousel_manage', methods=['GET'])
@login_required('admin')
def carousel_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    page = int(request.args.get('page', 1))
    per_page = 10
    pager = Carousel.query.order_by(Carousel.order_num.desc(), Carousel.id.desc()).paginate(page, per_page, False)
    return render_template('admin/entity/carousel_list.html', pager=pager)


@entity.route('/add_carousel', methods=['GET', 'POST'])
@login_required('admin')
def add_carousel():
    carousel_num = Carousel.query.count()
    if carousel_num >= settings['CAROUSEL_NUM_LIMIT']:
        flash(u'轮播最多为%d个，只有删除后才可以继续添加' % settings['CAROUSEL_NUM_LIMIT'])
        return redirect(url_for('admin_entity.carousel_manage'))

    if request.method == 'POST':
        title = request.form['title'].strip()

        image_file = request.files['image']
        full_image_url = ''
        if image_file.filename:
            image_folder = time.strftime('%Y%m', time.localtime())
            image_name = str(uuid.uuid4()) + '.'
            image_name = media.save(image_file, folder=image_folder, name=image_name)
            full_image_url = media.url(image_name)
            full_image_root = media.path(image_name)
            if not check_image_size(full_image_root, *settings['CAROUSEL_IMG_SIZE']):
                flash(u'添加失败，图片尺寸必须为%s' % str(settings['CAROUSEL_IMG_SIZE']))
                return redirect(url_for('admin_entity.add_carousel'))

        carousel = Carousel(title, full_image_url)
        if carousel_num == 0:
            carousel.order_num = 1
        else:
            carousel.order_num = db.session.query(func.max(Carousel.order_num)).scalar() + 1
        db.session.add(carousel)
        db.session.commit()

        flash(u'轮播添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.carousel_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_carousel'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/add_carousel.html')


@entity.route('/edit_carousel', methods=['GET', 'POST'])
@entity.route('/edit_carousel/<int:carousel_id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_carousel(carousel_id):
    carousel = Carousel.query.get(carousel_id)
    if request.method == 'POST':
        title = request.form['title'].strip()

        carousel.title = title

        image_file = request.files['image']
        if image_file.filename:
            image_folder = time.strftime('%Y%m', time.localtime())
            image_name = str(uuid.uuid4()) + '.'
            image_name = media.save(image_file, folder=image_folder, name=image_name)
            full_image_url = media.url(image_name)
            full_image_root = media.path(image_name)
            if not check_image_size(full_image_root, *settings['CAROUSEL_IMG_SIZE']):
                flash(u'添加失败，图片尺寸必须为%s' % str(settings['CAROUSEL_IMG_SIZE']))
                return redirect(url_for('admin_entity.add_carousel'))
            carousel.image = full_image_url
        db.session.commit()

        flash(u'轮播更新成功')
        return redirect(url_for('admin_entity.carousel_manage'))

    g.breadcrumbs = [u'信息管理', u'编辑信息']
    g.menu = 'entity'
    return render_template('admin/entity/edit_carousel.html', carousel=carousel)


@entity.route('/json/delete_carousel', methods=['POST'])
@login_required('admin')
def delete_carousel():
    carousel_id = int(request.form['carousel_id'])

    carousel = Carousel.query.get(carousel_id)
    db.session.delete(carousel)
    db.session.commit()
    flash(u'轮播删除成功')

    return jsonify(SUCCESS_MESSAGE)


########################################################################################################################
@entity.route('/region_manage', methods=['GET'])
@login_required('admin')
def region_manage():
    g.breadcrumbs = [u'信息管理']
    g.menu = 'entity'

    page = int(request.args.get('page', 1))
    per_page = 10
    pager = Region.query.order_by(Region.order_num.desc(), Region.id.desc()).paginate(page, per_page, False)
    return render_template('admin/entity/region_list.html', pager=pager)


@entity.route('/add_region', methods=['GET', 'POST'])
@login_required('admin')
def add_region():
    if request.method == 'POST':
        name = request.form['name'].strip()

        region = Region(name)
        db.session.add(region)
        db.session.commit()

        flash(u'地区添加成功')
        if request.form['_actionBtn'] == '1':
            return redirect(url_for('admin_entity.region_manage'))
        elif request.form['_actionBtn'] == '2':
            return redirect(url_for('admin_entity.add_region'))

    g.breadcrumbs = [u'信息管理', u'添加新信息']
    g.menu = 'entity'
    return render_template('admin/entity/add_region.html')


@entity.route('/edit_region', methods=['GET', 'POST'])
@entity.route('/edit_region/<int:region_id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_region(region_id):
    region = Region.query.get(region_id)
    if request.method == 'POST':
        name = request.form['name'].strip()

        region.name = name
        db.session.commit()

        flash(u'地区更新成功')
        return redirect(url_for('admin_entity.region_manage'))

    g.breadcrumbs = [u'信息管理', u'编辑信息']
    g.menu = 'entity'
    return render_template('admin/entity/edit_region.html', region=region)


@entity.route('/json/delete_region', methods=['POST'])
@login_required('admin')
def delete_region():
    region_id = int(request.form['region_id'])

    region = Region.query.get(region_id)
    db.session.delete(region)
    db.session.commit()
    flash(u'地区删除成功')

    return jsonify(SUCCESS_MESSAGE)


########################################################################################################################
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
    prev_name = request.args.get('prev_name')

    is_unique = (prev_name == name)
    if not is_unique:
        is_unique = (Region.query.filter(Region.name == name).count() == 0)

    return json.dumps(is_unique)


@entity.route('/json/check_building_unique', methods=['GET'])
@login_required('admin')
def check_building_unique():
    name = request.args['name'].strip()
    prev_name = request.args.get('prev_name')

    is_unique = (prev_name == name)
    if not is_unique:
        is_unique = (Building.query.filter(Building.name == name).count() == 0)

    return json.dumps(is_unique)


@entity.route('/json/exchange_carousel_pos', methods=['POST'])
def exchange_carousel_pos():
    try:
        last_id = request.form['last_id']
        current_id = request.form['current_id']
        last = Carousel.query.get(last_id)
        current = Carousel.query.get(current_id)
        last.order_num, current.order_num = current.order_num, last.order_num
        db.session.commit()

        return jsonify(SUCCESS_MESSAGE)
    except:
        return jsonify(ERROR_MESSAGE)
