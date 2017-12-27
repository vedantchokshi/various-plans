from flask import Blueprint
from . import jsonify_decorator
from .. import db

ROUTES = Blueprint('event', __name__)


@ROUTES.route('/<eventid>', methods=['GET'])
@jsonify_decorator
def events_get(eventid):
    return db.events.get_from_id(eventid)
