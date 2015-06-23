# -*- coding: utf-8 -*-
import os
import logging
import urlparse
from datetime import timedelta
from flask import url_for

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(levelname)s: %(message)s',
)

BASE_URL = ''
BASE_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_BASE_ROOT = os.path.join(BASE_ROOT, 'static/')
STATIC_BASE_URL = '/static/'
BUILDING_LOGO_DEFAULT = urlparse.urljoin(STATIC_BASE_URL, 'img/building_logo_default.jpg')
BUILDING_LOGO_SIZE = (168, 172)
CAROUSEL_IMG_DEFAULT = urlparse.urljoin(STATIC_BASE_URL, 'img/carousel_img_default.jpg')
CAROUSEL_IMG_SIZE = (640, 330)
CAROUSEL_NUM_LIMIT = 4
STARTPAGE_IMG_DEFAULT = urlparse.urljoin(STATIC_BASE_URL, 'img/carousel_img_default.jpg')
STARTPAGE_IMG_SIZE = (640, 330)

# Cookie secret
SECRET_KEY = 'dX6mg0jx0y`8(F_|Cp(#zUQTSAX_y<Q0%^W*#Q7<Wwyb2$^9CB4f<J>7Q~*#{&F~'

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/yuanyang'
SQLALCHEMY_ECHO = False
SQLALCHEMY_RECORD_QUERIES = False
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_POOL_TIMEOUT = 10
SQLALCHEMY_POOL_RECYCLE = 2 * 60 * 60
SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# WTForms
WTF_CSRF_ENABLED = False

# Flask Uploads
UPLOADS_DEFAULT_DEST = STATIC_BASE_ROOT
UPLOADS_DEFAULT_URL = STATIC_BASE_URL
UPLOADS_ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png')
