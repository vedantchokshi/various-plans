from flask import Blueprint, request
import back_end as be

ROUTES = Blueprint('plans', __name__)


@ROUTES.route('', methods=['GET'])
def plans_get():
    # /api/plans?id=<id>
    if request.args.has_key('id'):
        # We know id exists, try to cast to int
        id = request.args.get('id', type=int)
        # If ID cannot be cast to an it, id=None
        if not id:
            # id was not a number, complain accordingly
            return '400: Argument id is not an integer'
        if id < 0:
            # id must be positive integer
            return '400: Argument id is not positive'
        # We are now happy the id is good
        plan = be.plans.get_from_id(id)
        if not plan:
            return 'No plan with id: ' + str(id)
        else:
            # TODO convert to json
            return str(vars(plan))

    # No filter specified, REST would return everything but we just error
    return '400: Plan resource id not specified'
