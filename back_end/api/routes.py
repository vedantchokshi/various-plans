from flask import Blueprint, request

from back_end.api import jsonify_decorator
from back_end.api.api_exceptions import InvalidContent
from back_end.db import routes, route_events

ROUTES = Blueprint('route', __name__)


@ROUTES.route('/<routeid>', methods=['GET'])
@jsonify_decorator
def get_route(routeid):
    return routes.get_from_id(routeid), 200


@ROUTES.route('/<routeid>/events', methods=['GET'])
@jsonify_decorator
def get_events_from_route(routeid):
    # events don't preserve order, use route.eventids to get order
    return routes.get_from_id(routeid).events, 200


@ROUTES.route('/<routeid>/vote', methods=['POST'])
@jsonify_decorator
def vote_route(routeid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route vote object")
    return routes.update(routeid, json.get('vote')), 201


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
def create_route():
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route object")
    return routes.create(json.get('planid'), json.get('name'), json.get('eventidList')), 201
