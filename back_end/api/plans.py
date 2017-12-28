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
    # Needs a routes.get_from_planid
    return db.plans.get_from_id(planid)


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
def plans_get(planid):
    # Needs a events.get_from_planid
    return db.plans.get_from_id(planid)


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
def plans_create():
    json = request.json
    # I think json is a dict but you'll need to check
    return db.plans.create(json)
