"""
Provides RESTful URLs for Route objects
"""
from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import routes
from back_end.exceptions import InvalidContent

ROUTES = Blueprint('route', __name__)


@ROUTES.route('/<routeid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_route(routeid, userid):
    """
    Returns the route in JSON format with the `routeid` provided in URL.
    """
    return routes.get_from_id(routeid, userid), 200


@ROUTES.route('/<routeid>/events', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_events_from_plan(routeid, userid):
    """
    Returns the list of events in JSON format containing all events
    belonging to a route with the `routeid` provided in URL.
    """
    return routes.get_from_id(routeid, userid).events, 200


@ROUTES.route('/<routeid>/vote', methods=['POST'])
@jsonify_decorator
@token_decorator
def vote_route(routeid, userid):
    """
    Updates user's vote on the route specified by `routeid` provided in URL.
    Vote is extracted in a JSON object received in request.
    Returns the updated route in JSON format.
    """
    json = request.get_json()
    if json is None:
        raise InvalidContent("A problem occurred when voting on the route")
    return routes.vote(routeid, userid, json.get('vote')), 201


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_route(userid):
    """
    Creates a route with the properties specified in JSON object recieved in request.
    Returns the created route in JSON format.
    """
    json = request.get_json()
    if json is None:
        raise InvalidContent("A problem occurred when creating the route")
    return routes.create(json.get('planid'), json.get('name'), json.get('eventidList'), userid), 201
