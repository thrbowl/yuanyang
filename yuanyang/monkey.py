# -*- coding: utf-8 -*-
import sys
from functools import wraps
from types import FunctionType
from flask import current_app
from flask.ext.login import current_user


def role_required_noargs(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated():
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin():
            raise RuntimeError('Access is forbidden')
        return func(*args, **kwargs)

    return decorated_view


def role_required_args(role_list=None):
    def _role_required(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_app.login_manager._login_disabled:
                return func(*args, **kwargs)
            elif not current_user.is_authenticated():
                return current_app.login_manager.unauthorized()
            elif not current_user.is_admin():
                for role in role_list:
                    if current_user.has_role(role):
                        return func(*args, **kwargs)
                raise RuntimeError('Access is forbidden')
            return func(*args, **kwargs)

        return decorated_view

    return _role_required


def _dispatch_required(x=None):
    if type(x) == FunctionType:
        return role_required_noargs(x)
    elif x is None:
        return role_required_noargs
    elif type(x) == list:
        return role_required_args(x)
    else:
        raise ValueError('The argument is invalid')


def patch_login_required():
    sys.modules['flask.ext.login'].role_required = _dispatch_required


def patch_all():
    patch_login_required()
