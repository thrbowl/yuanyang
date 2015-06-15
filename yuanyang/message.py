def _message(func):
    def wrapper(self, content, **data):
        assert func.func_name in self.types, "Invalid method"
        return {
            'type': func.func_name,
            'content': content,
            'data': data
        }
    return wrapper


class _Message(object):
    types = ('success', 'error', 'warn')

    @_message
    def success(self, content, **data):
        pass

    @_message
    def error(self, content, **data):
        pass

    @_message
    def warn(self, content, **data):
        pass


message = _Message()
SUCCESS_MESSAGE = message.success('Operate successful')
ERROR_MESSAGE = message.error('Operate failure')
