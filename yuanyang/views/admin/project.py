# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, redirect, g, request, flash, json
from flask.ext.login import login_required, current_user
from ...models import *
from ...message import SUCCESS_MESSAGE, ERROR_MESSAGE

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
@project.route('/building_list/<int:area_id>', methods=['GET'])
@login_required('admin')
def building_list(area_id=None):
    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'楼盘列表', url_for('admin_project.building_list'))
    ]
    g.menu = 'project'

    area_list = Area.query.join(Building).order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    if area_id:
        area = Area.query.get(area_id)
    else:
        area = area_list[0]
    return render_template('admin/project/building_list.html', area=area, area_list=area_list)


@project.route('/view_building', methods=['GET'])
@project.route('/view_building/<int:building_id>', methods=['GET'])
@login_required
def view_building(building_id=None):
    business_scope = int(request.args.get('business_scope', -1))
    price_range = int(request.args.get('price_range', -1))
    status = int(request.args.get('status', -1))
    today = datetime.date.today()
    today_before_30 = str(today + datetime.timedelta(-30))
    today_after_30 = str(today + datetime.timedelta(30))
    publish_date_begin = request.args.get('publish_date_begin', today_before_30)
    publish_date_end = request.args.get('publish_date_end', today_after_30)

    if not building_id:
        building_id = int(request.args['building_id'])
    building = Building.query.get(building_id)
    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'楼盘列表', url_for('admin_project.building_list')),
        (u'%s·%s' % (building.area.name, building.name),
         url_for('admin_project.view_building', building_id=building_id))
    ]
    g.menu = 'project'

    if current_user.is_superuser:
        building_list = Building.query.join(Area).order_by(Area.order_num.desc(), Building.create_date.desc()).all()
    else:
        building_list = current_user.buildings

    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()

    page = int(request.args.get('page', 1))
    per_page = 15
    query = Project.query.filter(
        Project.building_id == building.id
    )
    if business_scope != -1:
        query = query.filter(Project.type_id == business_scope)
    if status in PROJECT_STATUS_LIST:
        query = query.filter(Project._status == status)
    if price_range in PROJECT_PRICE_RANGE_LIST:
        query = query.filter(Project._price_range == price_range)
    if publish_date_begin:
        query = query.filter(Project.publish_date >= publish_date_begin)
    if publish_date_end:
        query = query.filter(Project.publish_date <= publish_date_end)
    pager = query.order_by(Project.due_date.desc()).paginate(page, per_page, False)

    return render_template(
        'admin/project/view_building.html',
        price_range=price_range,
        status=status,
        business_scope=business_scope,
        publish_date_begin=publish_date_begin,
        publish_date_end=publish_date_end,
        building=building,
        building_list=building_list,
        price_range_list=PROJECT_PRICE_RANGE_LIST,
        status_list=PROJECT_STATUS_LIST,
        business_scope_list=business_scope_list,
        pager=pager,
        Project=Project
    )


@project.route('/view_project', methods=['GET'])
@project.route('/view_project/<int:project_id>', methods=['GET'])
@login_required
def view_project(project_id):
    project1 = Project.query.get(project_id)
    building = project1.building
    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'楼盘列表', url_for('admin_project.building_list')),
        (u'%s·%s' % (building.area.name, building.name),
         url_for('admin_project.view_building', building_id=building.id)),
        (project1.name, '#')
    ]
    g.menu = 'project'

    return render_template(
        'admin/project/view_project.html',
         project=project1,
         Project=Project
    )


@project.route('/add_project', methods=['GET', 'POST'])
@login_required
@catch_db_error
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
        project.name = name
        project.user_id = current_user.id
        project.building_id = building_id
        project.type_id = business_scope_id
        project.price_range = price_range
        project.requirements = requirements
        if due_date:
            project.due_date = due_date
        if lead_start_date:
            project.lead_start_date = lead_start_date
        if lead_end_date:
            project.lead_end_date = lead_end_date

        if request.form['_actionBtn'] == '1':
            result = project.publish()
            if result:
                db.session.add(project)
                db.session.commit()

                flash(u'发布成功')
                return redirect(url_for('admin_project.view_project', project_id=project.id))
            else:
                db.session.add(project)
                db.session.commit()

                flash(u'发布失败, 请修改数据后重新发布')
                return redirect(url_for('admin_project.edit_project', project_id=project.id))
        elif request.form['_actionBtn'] == '2':
            db.session.add(project)
            db.session.commit()

            flash(u'保存成功')
            return redirect(url_for('admin_project.draft_list'))

    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'创建新项目', url_for('admin_project.add_project'))
    ]
    g.menu = 'project'
    if current_user.is_superuser:
        building_list = Building.query.join(Area).order_by(Area.order_num.desc(), Building.create_date.desc()).all()
    else:
        building_list = current_user.buildings

    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()

    return render_template(
        'admin/project/add_project.html',
        building_list=building_list,
        business_scope_list=business_scope_list,
        price_range_list=PROJECT_PRICE_RANGE_LIST
    )


@project.route('/draft_list', methods=['GET'])
@login_required
def draft_list():
    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'创建新项目', url_for('admin_project.add_project')),
        (u'项目草稿箱', url_for('admin_project.draft_list'))
    ]
    g.menu = 'project'

    project_list = current_user.get_project_drafts()
    return render_template('admin/project/draft_list.html', project_list=project_list)


@project.route('/edit_project', methods=['GET', 'POST'])
@project.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@catch_db_error
def edit_project(project_id):
    project = Project.query.get(project_id)
    if request.method == 'POST':
        building_id = int(request.form['building'])
        business_scope_id = int(request.form['business_scope'])
        name = request.form['name'].strip()
        due_date = request.form['due_date'].strip()
        lead_start_date = request.form['lead_start_date'].strip()
        lead_end_date = request.form['lead_end_date'].strip()
        price_range = int(request.form['price_range'])
        requirements = request.form['requirements']

        project.name = name
        project.user_id = current_user.id
        project.building_id = building_id
        project.type_id = business_scope_id
        project.price_range = price_range
        project.requirements = requirements
        if due_date:
            project.due_date = due_date
        if lead_start_date:
            project.lead_start_date = lead_start_date
        if lead_end_date:
            project.lead_end_date = lead_end_date

        if request.form['_actionBtn'] == '1':
            result = project.publish()
            if result:
                db.session.commit()

                flash(u'发布成功')
                return redirect(url_for('admin_project.view_project', project_id=project.id))
            else:
                db.session.commit()

                flash(u'发布失败, 请修改数据后重新发布')
                return redirect(url_for('admin_project.edit_project', project_id=project.id))
        elif request.form['_actionBtn'] == '2':
            db.session.commit()

            flash(u'保存成功')
            return redirect(url_for('admin_project.draft_list'))

    g.breadcrumbs = [
        (u'项目管理', url_for('admin_project.index')),
        (u'编辑项目', '#')
    ]
    g.menu = 'project'
    if current_user.is_superuser:
        building_list = Building.query.join(Area).order_by(Area.order_num.desc(), Building.create_date.desc()).all()
    else:
        building_list = current_user.buildings

    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()
    return render_template(
        'admin/project/edit_project.html',
        project=project,
        building_list=building_list,
        business_scope_list=business_scope_list,
        price_range_list=PROJECT_PRICE_RANGE_LIST
    )


@project.route('/json/delete_project', methods=['POST'])
@login_required
@catch_db_error
def delete_project():
    project_id = int(request.form['project_id'])

    project = Project.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    flash(u'删除成功')

    return jsonify(SUCCESS_MESSAGE)


@project.route('/json/publish_project', methods=['POST'])
@project.route('/json/publish_project/<int:project_id>', methods=['POST'])
@login_required
@catch_db_error
def publish_project(project_id):
    project = Project.query.get(project_id)

    if not project.is_completed():
        flash(u'项目信息不完整，发布失败')
        return json.dumps(False)

    result = project.publish()
    db.session.commit()
    if result:
        flash(u'发布成功')
    else:
        flash(u'发布失败')
    return json.dumps(result)
