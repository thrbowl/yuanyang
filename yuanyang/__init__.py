# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask, render_template, url_for
from flask.ext.login import LoginManager
from . import monkey

monkey.patch_all()


def create_app(name=None, settings=None):
    """http://flask.pocoo.org/docs/patterns/appfactories/"""
    app = Flask(name or __name__)

    with app.app_context():
        # register settings
        # priority: params > settings.py > env variable
        app.config.from_envvar('YY_SETTINGS', silent=True)
        app.config.from_pyfile('settings.py')
        if settings is not None:
            if isinstance(object, settings):
                app.config.from_object(settings)
            elif os.path.isfile(os.path.join(app.root_path, settings)):
                app.config.from_pyfile(settings)

        logging.debug('Add global templates function')
        app.jinja_env.globals['static'] = (lambda filename: url_for('static', filename=filename))
        app.jinja_env.add_extension('jinja2.ext.do')

        logging.debug('Register error process handlers')

        @app.errorhandler(404)
        def http404(error):
            return render_template('404.html'), 404

        @app.errorhandler(500)
        def http500(error):
            return render_template('500.html'), 500

        logging.debug('Add user login manager')
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'admin_auth.login'

        @login_manager.user_loader
        def user_loader(user_id):
            from .models import User
            return User.query.get(user_id)

        logging.debug('Initialize the database')
        from .models import db

        db.init_app(app)

        logging.debug('Register blueprints')
        from .views.admin.main import main
        app.register_blueprint(main, url_prefix='/admin')
        from .views.admin.auth import auth
        app.register_blueprint(auth, url_prefix='/admin/auth')
        from .views.admin.entity import entity
        app.register_blueprint(entity, url_prefix='/admin/data')
        from .views.admin.project import project
        app.register_blueprint(project, url_prefix='/admin/project')
        from .views.admin.supplier import supplier
        app.register_blueprint(supplier, url_prefix='/admin/supplier')
        from .views.admin.user import user
        app.register_blueprint(user, url_prefix='/admin/user')

        from .views.api.supplier import supplier
        app.register_blueprint(supplier, url_prefix='/api/supplier')

        return app
