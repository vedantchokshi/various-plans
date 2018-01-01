from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.exceptions import InvalidContent
from back_end.db import events


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
        raise InvalidContent("Empty json not a valid event vote object")
    if not authenticate_user(eventid, userid):
        raise Unauthorized('Access Denied')

    # AUTHTODO -  I dont know how voting fully works with the method called in /db but I have some logic that can be used below

    var existingVote = # AUTHTODO - get users current vote from usereventvotes.vote
    var newVote = json.get('vote') # or get this in the logic method thats using it not from the json
    var changeToVote = newVote - existingVote
    # AUTHTODO - change the vote (lets call it v) of the event with id of eventid to v+changeToVote (this works for all cases)
    # AUTHTODO - set the users vote on this event (usereventvote.vote) to newVote
    # AUTHTODO - Add the current users vote on the event/route to the json { result: [ {id: int, planid: string, name: string, locationid: string, votes: int, userVoteState: -1 or 0 or 1} ] }
    
    # You may want to pass userid in here and do all the logic in events.vote - but i dont understand
    return events.vote(eventid, json.get('vote')), 201 # Add userid parameter here and in the method defintion


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_event(userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid event object")
    return events.create(json.get('planid'), json.get('name'), json.get('locationid'), userid), 201
