# -*- coding: utf-8 -*-
import sys
from functools import wraps
from types import FunctionType
from flask import current_app
from flask.ext.login import login_required, current_user


# the decorator login_required from flask login
def role_required(role):
    def _role_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_app.login_manager._login_disabled:
                return func(*args, **kwargs)
            elif not current_user.is_authenticated():
                return current_app.login_manager.unauthorized()
            elif role == 'admin' and current_user.is_superuser:
                return func(*args, **kwargs)
            raise RuntimeError('Access is forbidden')

        return decorated_view

    return _role_required


def _dispatch_required(x=None):
    if type(x) == FunctionType:
        return login_required(x)
    elif isinstance(x, basestring):
        return role_required(x)
    elif x is None:
        return login_required
    else:
        raise ValueError('The argument is invalid')


def patch_login_required():
    sys.modules['flask.ext.login'].login_required = _dispatch_required


def patch_all():
    patch_login_required()
