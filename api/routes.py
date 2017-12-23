from flask import Blueprint, request

ROUTES = Blueprint('routes', __name__)


@ROUTES.route('', methods=['GET'])
def routes_get():
    if request.args.has_key('id') and request.args.has_key('planid'):
        # both id and planid exist, doesn't make sense
        return '400: Too many arguments specified'
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
        return 'Route with id {}'.format(id)

    if request.args.has_key('planid'):
        # We know planid exists, try to cast to int
        planid = request.args.get('planid', type=int)
        # If plan ID cannot be cast to an it, id=None
        if not planid:
            # id was not a number, complain accordingly
            return '400: Argument planid is not an integer'
        if planid < 0:
            # id must be positive integer
            return '400: Argument planid is not positive'
        # We are now happy the id is good
        # Do db tings
        return 'List of routes with planid {}'.format(planid)

    # No filter specified, REST would return everything but we just error
    return '400: Route resource id or planid not specified'
