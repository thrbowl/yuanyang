# -*- coding: utf-8 -*-
import hashlib
import base64
import random
import string
import time
import uuid
from functools import wraps
from PIL import Image
from flask import json, Response, current_app
from flask.ext.login import current_user
from flask.ext.uploads import UploadSet, configure_uploads
from .message import message

SALT_CHARS = string.ascii_letters + string.digits

settings = current_app.config
media = UploadSet(name='media', extensions=settings['UPLOADS_ALLOWED_EXTENSIONS'])
configure_uploads(current_app, media)


def remove_if_endswith(str, *args):
    """Remove the specified string in list when it endswith the string"""
    for suffix in args:
        if str.endswith(suffix):
            return str[:-len(suffix)]
    return str


def remove_if_startwith(str, *args):
    """Remove the specified string in list when it startswith the string"""
    for prefix in args:
        if str.startswith(prefix):
            return str[len(prefix):]
    return str


def rand_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_hash_salt(password, method='sha1', hash_encoding='base64', salt_length=8, salt=None):
    """Generate the has and salt for given password"""
    salt = salt or ''.join(
        (random.choice(SALT_CHARS) for i in range(salt_length))
    )
    hash_method = getattr(hashlib, method)
    hash = hash_method((password + salt).encode('utf-8')).digest()
    if hash_encoding is None:
        enc_method = lambda x: x
    elif hash_encoding[:4] == 'base':
        def enc_method(value):
            base_method = getattr(
                base64, 'b{0}encode'.format(hash_encoding[4:])
            )
            return base_method(value).decode('ascii')
    return enc_method(hash), salt


def upload_image(fs, width=None, height=None):
    image_folder = time.strftime('%Y%m', time.localtime())
    image_name = str(uuid.uuid4()) + '.'
    image_name = media.save(fs, folder=image_folder, name=image_name)
    full_image_url = media.url(image_name)
    full_image_root = media.path(image_name)

    if width and height:
        with Image.open(full_image_root) as img:
            img.thumbnail((width, height), Image.ANTIALIAS)
            img.save(full_image_root)

    return full_image_url


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated():
            return jsonify(message.error(u'用户未登录'))
        return func(*args, **kwargs)
    return decorated_view


def convert_to_timestamp(dt):
    return dt.strftime("%s000")


def jsonify(data):
    return Response(json.dumps(data), mimetype='application/json')
