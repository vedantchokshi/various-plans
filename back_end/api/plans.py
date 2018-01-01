from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.exceptions import InvalidContent
from back_end.db import plans


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
    # AUTHTODO - Add the current users vote on the event/route to the json { result: [ {id: int, planid: string, name: string, locationid: string, votes: int, userVoteState: -1 or 0 or 1} ] }
    # Not sure how you want to deal with this, probably going to require another method.
    return plans.get_from_id(planid, userid).events, 200


@ROUTES.route('/<planid>/routes', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_routes_from_plan(planid, userid):
    # AUTHTODO - Add the current users vote on the event/route to the json { result: [ {id: int, planid: string, name: string, eventIdList: [eventid: int], votes: int, userVoteState: -1 or 0 or 1} ] }
    # Not sure how you want to deal with this, probably going to require another method.
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
