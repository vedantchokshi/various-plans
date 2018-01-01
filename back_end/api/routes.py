from flask import Blueprint, request

from back_end.api import jsonify_decorator, token_decorator
from back_end.exceptions import InvalidContent
from back_end.db import routes


ROUTES = Blueprint('route', __name__)


@ROUTES.route('/<routeid>', methods=['GET'])
@jsonify_decorator
@token_decorator
def get_route(routeid, userid):
    return routes.get_from_id(routeid, userid), 200


@ROUTES.route('/<routeid>/vote', methods=['POST'])
@jsonify_decorator
@token_decorator
def vote_route(routeid, userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route vote object")
    if not authenticate_user(routeid, userid):
        raise Unauthorized('Access Denied')

     # AUTHTODO - I dont know how voting fully works with the method called in /db but I have some logic that can be used below

    var existingVote = # AUTHTODO - get users current vote from userroutevotes.vote
    var newVote = json.get('vote') # or get this in the logic method thats using it not from the json
    var changeToVote = newVote - existingVote
    # AUTHTODO - change the vote (lets call it v) of the route with id of routeid to v+changeToVote (this works for all cases)
    # AUTHTODO - set the users vote on this route (userroutevote.vote) to newVote
    # AUTHTODO - Add the current users vote on the event/route to the json { result: [ {id: int, planid: string, name: string, locationid: string, votes: int, userVoteState: -1 or 0 or 1} ] }
    
    # You may want to pass userid in here and do all the logic in routes.vote - but i dont understand
    return routes.vote(routeid, json.get('vote')), 201  # Add userid parameter here and in the method defintion


@ROUTES.route('', methods=['POST'])
@jsonify_decorator
@token_decorator
def create_route(userid):
    json = request.get_json()
    if json is None:
        raise InvalidContent("Empty json not a valid route object")
    return routes.create(json.get('planid'), json.get('name'), json.get('eventids'), userid), 201


# AUTHTODO - I think you wanted to add /api/route/<id>/events - make sure you also add authenicate_user check