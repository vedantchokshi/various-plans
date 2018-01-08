"""
Route object for working with database and route functions for API
"""
from back_end.db import DB, STR_LEN, plans, events as db_events
from back_end.db.route_events import get_eventids_from_routeid
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


def get_routes(plan):
    """
    Get all the routes associated with this plan.
    This list is filtered to the winning route if the plan is
    in phases 3 and 4.
    """
    if plan.timephase < 3:
        return plan.routes_all.all()
    routes = [x for x in plan.routes_all.all() if x.votes > 0]
    return [routes[0]] if routes else []


def count_routes(plan):
    """
    Get a count of all the positively voted routes associated with this plan.
    """
    #return len([x for x in plan.routes_all.all() if x.votes > 0])
    return len(plan.routes_all.all())


plans.Plan.routes = property(get_routes)
plans.Plan.routes_count = property(count_routes)


class Route(DB.Model):
    """
    Route object that represents an entry in the 'Routes' table

    :param name: name of route
    """
    __tablename__ = 'Routes'
    id = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STR_LEN), nullable=False)
    planid = DB.Column(DB.Integer, DB.ForeignKey('Plans.id'), nullable=False)

    plan = DB.relationship('Plan', backref=DB.backref('routes_all', lazy='dynamic'))
    events = DB.relationship('Event', secondary='Route_Event')

    def __init__(self, name):
        self.name = name
        self.user_vote_state = None

    @property
    def eventids(self):
        """
        :return: ordered list of event IDs associated with the route
        """
        return get_eventids_from_routeid(self.id)

    @property
    def serialise(self):
        """
        Used to create a dictionary for jsonifying

        :return: dictionary representation of Route object
        """
        result = dict()
        result['id'] = self.id
        result['name'] = self.name
        result['eventidList'] = self.eventids
        result['planid'] = self.planid
        result['votes'] = self.votes
        result['userVoteState'] = getattr(self, 'user_vote_state', False)
        return result


def get_from_id(routeid, userid):
    """
    Get a route object from an ID
    """
    if not str(routeid).isdigit():
        raise InvalidRequest("Route ID '{}' is not a valid ID".format(routeid))
    route = Route.query.get(routeid)
    if route is None:
        raise ResourceNotFound("There is no route with the ID '{}'".format(routeid))
    route.userVoteState = route.get_vote(userid)
    return route


def create(planid, name, eventid_list, userid):
    """
    Create a route object with input validation and commit the object to the database
    """
    if name is None or not name:
        raise InvalidContent('Please specify a name for the route')
    if len(name) > STR_LEN:
        raise InvalidContent("Route name is too long")
    if eventid_list is None or not eventid_list:
        raise InvalidContent('Please specify events for the route')
    if len(set(eventid_list)) != len(eventid_list):
        raise InvalidContent('A route cannot contain the same event more than once')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 2:
        raise InvalidRequest(
            "{} (Plan {}) is not in the route voting stage".format(plan.name, planid))
    if not len(plan.routes_all.all()) < 10:
        raise InvalidRequest(
            "No more than 10 routes can be added to {} (Plan {})".format(plan.name, planid))

    event_list = list()

    for eventid in eventid_list:
        event = db_events.get_from_id(eventid, userid)
        if event.planid != plan.id:
            raise InvalidContent("{} (Event {}) does not exist in {} (Plan {})"
                                 .format(event.name, event.id, plan.name, plan.id))
        if event not in plan.events:
            raise InvalidContent(
                "{} (Event {}) does not have enough votes".format(event.name, event.id))
        event_list.append(event)

    for route in plan.routes:
        if eventid_list == route.eventids:
            raise InvalidContent(
                "This route has already been suggested under the name '{}'".format(route.name),
                content={'routeid': route.id})

    new_route = Route(name)
    # associate the route with a plan
    plan.routes_all.append(new_route)
    # associate all the events with the route
    new_route.events += event_list

    DB.session.commit()
    return new_route


def vote(routeid, userid, submitted_vote):
    """
    Add a vote from a user to a route
    """
    try:
        submitted_vote = int(submitted_vote)
        if not (submitted_vote >= -1 or submitted_vote <= 1):
            raise ValueError()
    except ValueError:
        raise InvalidContent("Vote '{}' is not a valid vote".format(submitted_vote))
    return get_from_id(routeid, userid).vote(userid, submitted_vote)
