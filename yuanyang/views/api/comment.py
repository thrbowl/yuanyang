# -*- coding: utf-8 -*-
from flask import Blueprint, request, json, jsonify, Response
from flask.ext.login import current_user
from ...models import *
from ...message import message as msgutil
from ...utils import login_required

comment = Blueprint('api_comment', __name__)


@comment.route('/comment', methods=['GET'])
@login_required
def comment_list():
    pass
    data = {}
    return Response(json.dumps(data), mimetype='application/json')
