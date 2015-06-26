# -*- coding: utf-8 -*-

def _message(func):
    def wrapper(self, content, **data):
        assert func.func_name in self.types, "Invalid method"
        return {
            'type': func.func_name,
            'status': func.func_name,
            'content': content,
            'msg': content,
            'data': data
        }
    return wrapper


class _Message(object):
    types = ('success', 'error', 'warn', 'ok')

    @_message
    def success(self, content, **data):
        pass

    @_message
    def error(self, content, **data):
        pass

    @_message
    def warn(self, content, **data):
        pass

    @_message
    def ok(self, content, **data):
        pass


message = _Message()
SUCCESS_MESSAGE = message.success(u'操作成功')
ERROR_MESSAGE = message.error(u'操作失败')
OK_MESSAGE = message.ok(u'操作成功')
