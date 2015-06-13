# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, g
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


@project.route('/view_building/<int:building_id>', methods=['GET'])
@login_required
def view_building(building_id):
    building = Building.query.get(building_id)
    g.breadcrumbs = [u'项目管理', u'楼盘列表', u'%s.%s' % (building.region.name, building.name)]
    g.menu = 'project'

    return render_template('admin/project/view_building.html', building=building)


@project.route('/view_project/<int:project_id>', methods=['GET'])
@login_required
def view_project(project_id):
    projec = Project.query.get(project_id)
    building = projec.building
    g.breadcrumbs = [u'项目管理', u'楼盘列表', u'%s.%s' % (building.region.name, building.name), projec.name]
    g.menu = 'project'
