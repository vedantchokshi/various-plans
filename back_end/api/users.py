"""
Provides RESTful URLs for User objects
"""
from flask import Blueprint

from back_end.api import jsonify_decorator, token_decorator
from back_end.db import plan_users

ROUTES = Blueprint('user', __name__)


@ROUTES.route('/plans')
@jsonify_decorator
@token_decorator
def get_plans_from_user(userid):
    """
    Returns the list of plans that the user with `userid` belongs to in JSON format.
    """
    return plan_users.get_plans(userid), 200
