# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, request, redirect, g, flash, jsonify, current_app
from flask.ext.login import login_required, current_user
from ...models import db, catch_db_error, Area, BusinessScope, Supplier, Project, Message
from ...message import SUCCESS_MESSAGE, ERROR_MESSAGE

supplier = Blueprint('admin_supplier', __name__)

settings = current_app.config


@supplier.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('admin_supplier.supplier_list'))


@supplier.route('/supplier_list', methods=['GET'])
@login_required
def supplier_list():
    sort = int(request.args.get('sort', 1))
    area = int(request.args.get('area', -1))
    business_scope = int(request.args.get('business_scope', -1))

    area_list = Area.query.join(Supplier).order_by(Area.order_num.desc(), Area.create_date.desc()).all()
    business_scope_list = BusinessScope.query.filter(BusinessScope.parent_id == None) \
        .order_by(BusinessScope.order_num.desc(), BusinessScope.create_date.desc()).all()

    page = int(request.args.get('page', 1))
    per_page = 15
    query = Supplier.query.join(Supplier.business_scopes).filter(
        Supplier._status == Supplier.STATUS_PASS
    )

    if area != -1:
        query = query.filter(Supplier.company_area_id == area)
    if business_scope != -1:
        query = query.filter(BusinessScope.id == business_scope)
    if sort == 1:
        query = query.order_by(Supplier.service_score.desc())
    elif sort == 2:
        query = query.order_by(Supplier.service_score.asc())
    pager = query.paginate(page, per_page, False)

    g.breadcrumbs = [
        (u'供应商管理', url_for('admin_supplier.index')),
        (u'供应商列表', '#')
    ]
    g.menu = 'supplier'
    return render_template(
        'admin/supplier/supplier_list.html',
        sort=sort,
        area=area,
        business_scope=business_scope,
        area_list=area_list,
        business_scope_list=business_scope_list,
        pager=pager
    )


@supplier.route('/audit_list', methods=['GET'])
@login_required('admin')
def audit_list():
    page = int(request.args.get('page', 1))
    per_page = 15
    pager = Supplier.query.join(Supplier.business_scopes).filter(
        Supplier._status == Supplier.STATUS_PENDING
    ).paginate(page, per_page, False)

    g.breadcrumbs = [
        (u'供应商管理', url_for('admin_supplier.index')),
        (u'新供应商审核', url_for('admin_supplier.audit_list'))
    ]
    g.menu = 'supplier'
    return render_template(
        'admin/supplier/audit_list.html',
        pager=pager
    )


@supplier.route('/view_supplier', methods=['GET'])
@supplier.route('/view_supplier/<int:supplier_id>', methods=['GET'])
@login_required
def view_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    project_list = Project.query.filter(Project.supplier_id == supplier.id,
                                        Project._status == Project.STATUS_COMMENTED).all()

    g.breadcrumbs = [
        (u'供应商管理', url_for('admin_supplier.index')),
        (u'供应商列表', url_for('admin_supplier.supplier_list')),
        (u'%s' % supplier.company_name, '#'),
    ]
    g.menu = 'supplier'
    return render_template(
        'admin/supplier/view_supplier.html',
        supplier=supplier,
        project_list=project_list
    )


@supplier.route('/audit_supplier', methods=['GET'])
@supplier.route('/audit_supplier/<int:supplier_id>', methods=['GET'])
@login_required('admin')
def audit_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)

    g.breadcrumbs = [
        (u'供应商管理', url_for('admin_supplier.index')),
        (u'新供应商审核', url_for('admin_supplier.audit_list')),
        (u'%s' % supplier.company_name, '#'),
    ]
    g.menu = 'supplier'
    return render_template(
        'admin/supplier/audit_supplier.html',
        supplier=supplier
    )


@supplier.route('/json/audit_pass', methods=['POST'])
@login_required
@catch_db_error
def audit_pass():
    supplier_id = int(request.form['supplier_id'])

    supplier = Supplier.query.get(supplier_id)
    supplier.status = Supplier.STATUS_PASS
    db.session.commit()

    try:
        message = Message(settings['MESSAGE_AUDIT_PASS'])
        message.type = Message.TYPE_SYSTEM
        message.receiver_id = supplier.id
        db.session.add(message)
        db.session.commit()
    except Exception, e:
        print 111, e

    flash(u'审核通过')
    return jsonify(SUCCESS_MESSAGE)


@supplier.route('/json/audit_reject', methods=['POST'])
@login_required
@catch_db_error
def audit_reject():
    supplier_id = int(request.form['supplier_id'])
    reason = request.form['reason'].strip()
    if not reason:
        reason = u'无'

    supplier = Supplier.query.get(supplier_id)
    supplier.status = Supplier.STATUS_NOTAUTH
    db.session.commit()

    try:
        message = Message(settings['MESSAGE_AUDIT_REJECT'])
        message.type = Message.TYPE_SYSTEM
        message.receiver_id = supplier.id
        db.session.add(message)
        db.session.commit()
    except Exception, e:
        print 111, e

    flash(u'审核未通过')
    return jsonify(SUCCESS_MESSAGE)
