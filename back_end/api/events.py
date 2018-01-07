from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import events
from back_end.exceptions import InvalidContent

ROUTES = Blueprint('event', __name__)


@ROUTES.route('/<eventid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_event(eventid, userid):
    return events.get_from_id(eventid, userid), 200


@ROUTES.route('/<eventid>/vote', methods=['POST'])
@jsonify_decorator
@token_decorator
def vote_event(eventid, userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("A problem occured when voting on the event.")
        #raise InvalidContent("Empty json not a valid event vote object")
    return events.vote(eventid, userid, json.get('vote')), 201


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_event(userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("A problem occured when creating the event.")
        #raise InvalidContent("Empty json not a valid event object")
    return events.create(json.get('planid'), json.get('name'), json.get('locationid'), userid), 201
