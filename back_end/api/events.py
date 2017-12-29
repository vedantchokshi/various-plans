from flask import Blueprint, request

from back_end.api import jsonify_decorator
from back_end.api.api_exceptions import InvalidContent
from back_end.db import events

ROUTES = Blueprint('event', __name__)


@ROUTES.route('/<eventid>', methods=['GET'])
@jsonify_decorator
def get_event(eventid):
    return events.get_from_id(eventid), 200


@ROUTES.route('/<eventid>/vote', methods=['POST'])
@jsonify_decorator
def vote_event(eventid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid event vote object")
    return events.update(eventid, json.get('vote')), 201


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
def create_event():
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid event object")
    return events.create(json.get('planid'), json.get('name'), json.get('locationid')), 201
