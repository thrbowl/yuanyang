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
BUILDING_LOGO_SIZE = (169, 172)
CAROUSEL_IMG_DEFAULT = urlparse.urljoin(STATIC_BASE_URL, 'img/carousel_img_default.jpg')
CAROUSEL_IMG_SIZE = (640, 330)
CAROUSEL_NUM_LIMIT = 4
STARTPAGE_IMG_DEFAULT = urlparse.urljoin(STATIC_BASE_URL, 'img/carousel_img_default.jpg')
STARTPAGE_IMG_SIZE = (640, 330)

CLOSURE_PERIOD = 7

# Cookie secret
SECRET_KEY = 'dX6mg0jx0y`8(F_|Cp(#zUQTSAX_y<Q0%^W*#Q7<Wwyb2$^9CB4f<J>7Q~*#{&F~'

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/yuanyang'
SQLALCHEMY_ECHO = True
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

# Message Template
MESSAGE_ADD_PROJECT = u'有符合您注册条件的新项目发布了，快去查看吧！'
MESSAGE_AUDIT_PASS = u'恭喜您通过了供应商资料审核，可以正常参与招商活动。'
MESSAGE_AUDIT_REJECT = u'很抱歉，您提交的资料的未通过审核，驳回理由为“%s”，请重新提交。'
MESSAGE_PROJECT_APPLY = u'您已成功参与【%s】项目报名，我们的工作人员随后会与您联系，请您耐心等待。'
MESSAGE_PROJECT_BID = u'恭喜您成为【%s】项目的中标单位。'
MESSAGE_PROJECT_NOT_BID = u'很遗憾，您未能成为【%s】项目的中标单位，感谢您的参与，请继续关注其他项目。'
MESSAGE_PROJECT_FAILURE = u'很遗憾，【%s】项目因【未选择合适供应商】原因流标，感谢您的参与，请继续关注我们的动态。'
MESSAGE_PROJECT_COMMENTED = u'您负责的【%s】项目得到了用户的评价，请前往查看详情。'
MESSAGE_PROJECT_COMPLETED = u'您负责的【%s】项目已经完成，请前往查看详情。'

MAIL_SERVER = 'smtp.126.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_DEBUG = True
MAIL_USERNAME = 'dxangle@126.com'
MAIL_PASSWORD = 'dx84296733'
MAIL_DEFAULT_SENDER = 'dxangle@126.com'
