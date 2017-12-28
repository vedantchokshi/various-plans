from flask import Blueprint, request
from . import jsonify_decorator
from .. import db

ROUTES = Blueprint('plan', __name__)


@ROUTES.route('/<planid>', methods=['GET'])
@jsonify_decorator
def plans_get(planid):
    return db.plans.get_from_id(planid)


@ROUTES.route('/<planid>/events', methods=['GET'])
@jsonify_decorator
def plans_get(planid):
    return db.plans.get_from_id(planid).events


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
def plans_get(planid):
    return db.plans.get_from_id(planid).routes


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
def plans_create():
    json = request.get_json()
    # I think json is a dict but you'll need to check
    return db.plans.create(json.get('name'))
