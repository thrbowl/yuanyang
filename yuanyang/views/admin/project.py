# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, g
from flask.ext.login import role_required
from ...models import *

project = Blueprint('admin_project', __name__)


@project.route('/building_list', methods=['GET'])
@role_required
def building_list():
    g.breadcrumbs = [u'项目管理', u'楼盘列表']
    region_list = Region.query.all()
    return render_template('admin/project/building_list.html', region_list=region_list)


@project.route('/view_building/<int:building_id>', methods=['GET'])
@role_required(['operator'])
def view_building(building_id):
    building = Building.query.get(building_id)
    g.breadcrumbs = [u'项目管理', u'楼盘列表', u'%s.%s' % (building.region.name, building.name)]
    return render_template('admin/project/view_building.html', building=building)


@project.route('/view_project/<int:project_id>', methods=['GET'])
@role_required(['operator'])
def view_project(project_id):
    pass
