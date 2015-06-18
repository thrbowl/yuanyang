# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, g, request, flash
from flask.ext.login import login_required, current_user
from ...models import *

project = Blueprint('admin_project', __name__)


@project.route('/', methods=['GET'])
@login_required
def index():
    if current_user.is_superuser:
        return redirect(url_for('admin_project.building_list'))
    else:
        building = current_user.buildings[0]
        return redirect(url_for('admin_project.view_building', building_id=building.id))


@project.route('/building_list', methods=['GET'])
@project.route('/building_list/<int:region_id>', methods=['GET'])
@login_required
def building_list(region_id=None):
    g.breadcrumbs = [u'项目管理', u'楼盘列表']
    g.menu = 'project'

    region_list = Region.query.all()
    if region_id:
        region = Region.query.get(region_id)
    else:
        region = region_list[0]
    return render_template('admin/project/building_list.html', region=region, region_list=region_list)


@project.route('/view_building', methods=['GET'])
@project.route('/view_building/<int:building_id>', methods=['GET'])
@login_required
def view_building(building_id):
    building = Building.query.get(building_id)
    g.breadcrumbs = [u'项目管理', u'楼盘列表', u'%s.%s' % (building.region.name, building.name)]
    g.menu = 'project'

    if current_user.is_superuser:
        building_list = Building.query.order_by(Building.order_num.desc(), Building.id.desc()).all()
    else:
        building_list = current_user.buildings

    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.id.desc()).all()

    return render_template(
        'admin/project/view_building.html',
        building=building,
        building_list=building_list,
        price_range_list=PROJECT_PRICE_RANGE_LIST,
        status_list=PROJECT_STATUS_LIST,
        business_scope_list=business_scope_list
    )


@project.route('/view_project', methods=['GET'])
@project.route('/view_project/<int:project_id>', methods=['GET'])
@login_required
def view_project(project_id):
    projec = Project.query.get(project_id)
    building = projec.building
    g.breadcrumbs = [u'项目管理', u'楼盘列表', u'%s.%s' % (building.region.name, building.name), projec.name]
    g.menu = 'project'


@project.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        building_id = int(request.form['building'])
        business_scope_id = int(request.form['business_scope'])
        name = request.form['name'].strip()
        due_date = request.form['due_date'].strip()
        lead_start_date = request.form['lead_start_date'].strip()
        lead_end_date = request.form['lead_end_date'].strip()
        price_range = int(request.form['price_range'])
        requirements = request.form['requirements']

        project = Project()
        project.user_id = current_user.id
        project.building_id = building_id
        project.type_id = business_scope_id
        project.price_range = price_range
        project.requirements = requirements
        if name:
            project.name = name
        if due_date:
            project.due_date = due_date
        if lead_start_date:
            project.lead_start_date = lead_start_date
        if lead_end_date:
            project.lead_end_date = lead_end_date

        if request.form['_actionBtn'] == '1':
            project.status = Project.STATUS_BIDDING
            project.publish_date = datetime.datetime.now()
            db.session.add(project)
            db.session.commit()
            flash(u'提交成功')
            return redirect(url_for('admin_project.view_project', project_id=project.id))
        elif request.form['_actionBtn'] == '2':
            project.status = Project.STATUS_DRAFT
            db.session.add(project)
            db.session.commit()
            flash(u'保存成功')
            return redirect("")

    g.breadcrumbs = [u'项目管理', u'创建新项目']
    g.menu = 'project'
    if current_user.is_superuser:
        building_list = Building.query.order_by(Building.order_num.desc(), Building.id.desc()).all()
    else:
        building_list = current_user.buildings

    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.id.desc()).all()

    return render_template(
        'admin/project/add_project.html',
        building_list=building_list,
        business_scope_list=business_scope_list,
        price_range_list=PROJECT_PRICE_RANGE_LIST
    )
