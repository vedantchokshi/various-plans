"""
Provides RESTful URLs for Plan objects
"""
from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import plans
from back_end.exceptions import InvalidContent

ROUTES = Blueprint('plan', __name__)


@ROUTES.route('/<planid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_plan(planid, userid):
    """
    Returns the plan in JSON format with the `planid` provided in URL.
    """
    return plans.get_from_id(planid, userid), 200


@ROUTES.route('/join/', defaults={'joinid': None})
@ROUTES.route('/join/<joinid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def join_plan(joinid, userid):
    """
    Adds a user with `userid` to the plan that has a join code of `joinid`
    Returns the plan in JSON format with the `planid` provided in URL.
    """
    return plans.add_user(joinid, userid), 200


@ROUTES.route('/<planid>/events', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_events_from_plan(planid, userid):
    """
    Returns the list of events in JSON format.
    List contains varing results dependant of phase:
        Phase 1: all events
        Phase 2-4: all events with positive number of votes
    belonging to a plan with the `planid` provided in URL.
    """
    return plans.get_events_from_id(planid, userid), 200


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_routes_from_plan(planid, userid):
    """
    Returns the list of routes in JSON format.
    List contains varing results dependant of phase:
        Phase 1: nothing
        Phase 2: all routes
        Phase 3-4: winning route
    belonging to a plan with the `planid` provided in URL.
    """
    return plans.get_routes_from_id(planid, userid), 200


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_plan(userid):
    """
    Creates a plan with the properties specified in the JSON object recieved in request.
    Returns the created plan in JSON format.
    """
    json = request.get_json()
    if json is None:
        raise InvalidContent("An problem occurred when creating the plan")
    return plans.create(json.get('name'), json.get('eventVoteCloseTime'),
                        json.get('routeVoteCloseTime'), json.get('endTime'), userid), 201
