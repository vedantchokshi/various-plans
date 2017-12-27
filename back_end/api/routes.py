from flask import Blueprint
from . import jsonify_decorator
from .. import db

ROUTES = Blueprint('route', __name__)


@ROUTES.route('/<routeid>', methods=['GET'])
@jsonify_decorator
def routes_get(routeid):
    return db.routes.get_from_id(routeid)
