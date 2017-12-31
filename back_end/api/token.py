from __future__ import print_function

from flask import Blueprint

from back_end.api import token_decorator

ROUTES = Blueprint('token', __name__)


@ROUTES.route('', methods=['POST'])
@token_decorator
def test_token(userid):
    return 'userid: {}'.format(userid)
