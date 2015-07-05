# -*- coding: utf-8 -*-
import time
import uuid
from flask import Blueprint, request
from flask.ext.login import current_user
from flask.ext.uploads import configure_uploads, UploadSet
from ...message import message
from ...models import *
from ...utils import jsonify, login_required


supplier = Blueprint('api_supplier', __name__)

settings = current_app.config
media = UploadSet(name='media', extensions=settings['UPLOADS_ALLOWED_EXTENSIONS'])
configure_uploads(current_app, media)


@supplier.route('/enterInfo', methods=['GET'])
@login_required
def get_supplier_info():
    type = request.args['type'].strip()

    supplier = current_user.supplier

    if type == 'auth':
        data = {
            'bl': supplier.business_licence,
            'blImgUrl': supplier.business_licence_image,
            'trc': supplier.tax_registration_certificate,
            'trcImgUrl': supplier.tax_registration_certificate_image,
            'occ': supplier.organization_code_certificate,
            'occImgUrl': supplier.organization_code_certificate_image,
        }
        return jsonify(data)
    elif type == 'base':
        data = {
            'companyName': supplier.company_name,
            'contactName': supplier.company_contact,
            'tel': supplier.company_contact_telephone,
            'position': supplier.area and supplier.area.full_name,
            'addrSpec': supplier.company_address,
            'bank': supplier.deposit_bank,
            'account': supplier.bank_account,
        }
        return jsonify(data)
    else:
        return jsonify(message.error(u'类型不正确'))


@supplier.route('/enterInfo', methods=['POST'])
@login_required
@catch_db_error
def update_supplier_info():
    company_name = request.form.get('companyName')
    company_contact = request.form.get('contactName')
    company_contact_telephone = request.form.get('tel')
    company_address = request.form.get('addrSpec')
    deposit_bank = request.form.get('bank')
    bank_account = request.form.get('account')
    business_licence = request.form.get('bl')
    tax_registration_certificate = request.form.get('trc')
    organization_code_certificate = request.form.get('occ')

    city = int(request.form.get('city', 0))
    business_scope_list = map(int, request.form.getlist('bs'))

    supplier = current_user.supplier
    if company_name:
        supplier.company_name = company_name
    if company_contact:
        supplier.company_contact = company_contact
    if company_contact_telephone:
        supplier.company_contact_telephone = company_contact_telephone
    if company_address:
        supplier.company_address = company_address
    if deposit_bank:
        supplier.deposit_bank = deposit_bank
    if bank_account:
        supplier.bank_account = bank_account
    if business_licence:
        supplier.business_licence = business_licence
    if tax_registration_certificate:
        supplier.tax_registration_certificate = tax_registration_certificate
    if organization_code_certificate:
        supplier.organization_code_certificate = organization_code_certificate
    if city:
        supplier.company_area_id = city
    if business_scope_list:
        supplier.business_scopes = [BusinessScope.query.get(bs_id) for bs_id in business_scope_list]

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
