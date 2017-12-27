from flask import Blueprint
from . import jsonify_decorator
from .. import db

ROUTES = Blueprint('plan', __name__)


@ROUTES.route('/<planid>', methods=['GET'])
@jsonify_decorator
def plans_get(planid):
    plan = db.plans.get_from_id(planid)
    if not plan:
        return 'No plan with id: ' + str(planid)
    else:
        return plan