# -*- coding: utf-8 -*-
import time, uuid
from flask import current_app, Blueprint, request, json, jsonify
from flask_login import current_user
from flask.ext.uploads import UploadSet, configure_uploads
from ...models import db, catch_db_error, Supplier, Area, BusinessScope
from ...utils import login_required
from ...message import message

supplier = Blueprint('api_supplier', __name__)

settings = current_app.config
media = UploadSet(name='media', extensions=settings['UPLOADS_ALLOWED_EXTENSIONS'])
configure_uploads(current_app, media)


@supplier.route('/enterInfo', methods=['POST'])
@login_required
@catch_db_error
def update_supplier_info():
    company_name = request.form['companyName']
    company_contact = request.form['contactName']
    company_contact_telephone = request.form['tel']
    company_address = request.form['addrSpec']
    deposit_bank = request.form['bank']
    bank_account = request.form['account']
    business_licence = request.form['bl']
    tax_registration_certificate = request.form['trc']
    organization_code_certificate = request.form['occ']

    province = request.form['province']
    city = request.form['city']
    business_scope_list = request.form.getlist('bs')

    supplier = current_user.supplier
    supplier.company_name = company_name
    supplier.company_contact = company_contact
    supplier.company_contact_telephone = company_contact_telephone
    supplier.company_address = company_address
    supplier.deposit_bank = deposit_bank
    supplier.bank_account = bank_account
    supplier.business_licence = business_licence
    supplier.tax_registration_certificate = tax_registration_certificate
    supplier.organization_code_certificate = organization_code_certificate
    try:
        province = Area.query.filter(Area.name == province).one()
        city = Area.query.filter(Area.parent == province.id, Area.name == city).one()
        supplier.company_area_id = city.id
    except:
        return jsonify(message.error(u'找不到该城市'))

    try:
        for bs in business_scope_list:
            bs = BusinessScope.query.filter(BusinessScope.name == bs).one()
            supplier.business_scopes.append(bs)
    except:
        return jsonify(message.error(u'无效的经营范围'))

    db.session.add(supplier)
    db.session.commit()

    return jsonify(message.ok(u'更新成功'))


@supplier.route('/enterInfoFile', methods=['POST'])
@login_required
@catch_db_error
def update_supplier_pic():
    business_licence_image = request.files['blFile']
    tax_registration_certificate_image = request.files['trcFile']
    organization_code_certificate_image = request.files['occFile']

    supplier = current_user.supplier

    image_folder = time.strftime('%Y%m', time.localtime())
    image_name = str(uuid.uuid4()) + '.'
    if business_licence_image.filename:
        image_name = media.save(business_licence_image, folder=image_folder, name=image_name)
        full_image_url = media.url(image_name)
        supplier.business_licence_image = full_image_url

    if tax_registration_certificate_image.filename:
        image_name = media.save(tax_registration_certificate_image, folder=image_folder, name=image_name)
        full_image_url = media.url(image_name)
        supplier.business_licence_image = full_image_url

    if organization_code_certificate_image.filename:
        image_name = media.save(organization_code_certificate_image, folder=image_folder, name=image_name)
        full_image_url = media.url(image_name)
        supplier.business_licence_image = full_image_url

    db.session.commit()

    return jsonify(message.ok(u'更新成功'))
