# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, url_for, request, session, json, jsonify
from flask.ext.login import login_required, redirect
from ...models import Supplier

supplier = Blueprint('api_supplier', __name__)
