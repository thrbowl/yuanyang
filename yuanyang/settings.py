# -*- coding: utf-8 -*-
import os
import logging
import urlparse
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s - %(levelname)s: %(message)s',
)

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
