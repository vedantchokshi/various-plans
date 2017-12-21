from flask import Blueprint

ROUTES = Blueprint('plans', __name__, static_folder='static', template_folder='templates')


@ROUTES.route("/")
def plans_all():
    return "List of all plans"


@ROUTES.route("/id/<planid>")
def plan_from_id(planid):
    return "Plan with id: {}".format(planid)
