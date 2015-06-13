# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, request
from flask.ext.login import login_required, login_user, redirect, logout_user, current_user
from ...forms import LoginForm
from ...models import db, User

auth = Blueprint('admin_auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    next = request.args.get('next', url_for('admin_main.index'))
    if current_user.is_authenticated():
        return redirect(next)

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(next)
    return render_template('admin/auth/login.html', form=form, next=next)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_auth.login'))
