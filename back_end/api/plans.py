from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import plans
from back_end.exceptions import InvalidContent

ROUTES = Blueprint('plan', __name__)


@ROUTES.route('/<planid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_plan(planid, userid):
    return plans.get_from_id(planid, userid), 200


@ROUTES.route('/<planid>/events', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_events_from_plan(planid, userid):
    return plans.get_from_id(planid, userid).events, 200


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_routes_from_plan(planid, userid):
    return plans.get_from_id(planid, userid).routes, 200


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_plan(userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid plan object")
    return plans.create(json.get('name'), json.get('eventVoteCloseTime'), json.get('routeVoteCloseTime'),
                        json.get('endTime'), userid), 201
