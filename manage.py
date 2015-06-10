# -*- coding: utf-8 -*-
from yuanyang import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from yuanyang.commands import manager
        manager.app = app
        manager.run()
