from flask import Blueprint, request
from . import jsonify_decorator
from .. import db

ROUTES = Blueprint('plan', __name__)


@ROUTES.route('/<planid>', methods=['GET'])
@jsonify_decorator
def get_plan(planid):
    return db.plans.get_from_id(planid)


@ROUTES.route('/<planid>/events', methods=['GET'])
@jsonify_decorator
def get_events_from_plan(planid):
    return db.plans.get_from_id(planid).events


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
def get_routes_from_plan(planid):
    return db.plans.get_from_id(planid).routes


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
def create_plan():
    json = request.get_json()
    # If keys don't exist, None is used
    return db.plans.create(json.get('name'), json.get('eventVoteCloseTime'), json.get('routeVoteCloseTime'),
                           json.get('startTime'), json.get('endTime'))
