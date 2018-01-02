from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import routes
from back_end.exceptions import InvalidContent

ROUTES = Blueprint('route', __name__)


@ROUTES.route('/<routeid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_route(routeid, userid):
    return routes.get_from_id(routeid, userid), 200


@ROUTES.route('/<routeid>/events', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_events_from_plan(routeid, userid):
    return routes.get_from_id(routeid, userid).events, 200


@ROUTES.route('/<routeid>/vote', methods=['POST'])
@jsonify_decorator
@token_decorator
def vote_route(routeid, userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route vote object")
    return routes.vote(routeid, userid, json.get('vote')), 201


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_route(userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route object")
    return routes.create(json.get('planid'), json.get('name'), json.get('eventids'), userid), 201
