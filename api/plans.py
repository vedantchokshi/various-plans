from flask import Blueprint, request

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
        # Do db tings
        return 'Plan with id {}'.format(id)

    # No filter specified, REST would return everything but we just error
    return '400: Plan resource id not specified'
