from __future__ import print_function

from back_end.db import DB, STR_LEN, plans, events as db_events
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


def get_routes_sql(plan):
    if plan.timephase < 3:
        return plan.routes_all.all()
    routes = [x for x in plan.routes_all.all() if x.votes > 0]
    return [routes[0]] if len(routes) > 0 else []


def count_positive_routes_sql(plan):
    return len([x for x in plan.routes_all.all() if x.votes > 0])


plans.Plan.routes = property(get_routes_sql)
plans.Plan.routes_count_positive = property(count_positive_routes_sql)


class Route(DB.Model):
    __tablename__ = 'Routes'
    id = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.String(STR_LEN), nullable=False)
    planid = DB.Column(DB.Integer, DB.ForeignKey('Plans.id'), nullable=False)
    # votes = db.Column(db.Integer, nullable=False)

    plan = DB.relationship('Plan', backref=DB.backref('routes_all', lazy='dynamic'))
    events = DB.relationship('Event', secondary='Route_Event')

    def __init__(self, name):
        self.name = name
        self.userVoteState = None

    @property
    def eventids(self):
        return [re.id for re in self.events]

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['eventidList'] = self.eventids
        s['votes'] = self.votes
        s['userVoteState'] = getattr(self, 'userVoteState', False)
        return s


def get_from_id(routeid, userid):
    if not str(routeid).isdigit():
        raise InvalidRequest("Route id '{}' is not a valid id".format(routeid))
    route = Route.query.get(routeid)
    if route is None:
        raise ResourceNotFound("There is no route with the ID '{}'".format(routeid))
        # raise ResourceNotFound("Route not found for id '{}'".format(routeid))
    route.userVoteState = route.get_vote(userid)
    return route


def create(planid, name, eventid_list, userid):
    if name is None or not name:
        raise InvalidContent('Please specify a name for the route.')
        # raise InvalidContent('Route name is not specified')
    if eventid_list is None:
        raise InvalidContent('Please specify events for the route.')
        # raise InvalidContent('Route eventidList is not specified')
    if len(eventid_list) == 0:
        raise InvalidContent('Please specify events for the route.')
        # raise InvalidContent('Route eventidList must have a non-zero size')
    if len(set(eventid_list)) != len(eventid_list):
        raise InvalidContent('A route cannot contain the same event more than once.')
        # raise InvalidContent('Route eventidList cannot repeat an event')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 2:
        raise InvalidRequest(
            "{} (Plan {}) is not in the route voting stage.".format(plan.name, planid))
        # raise InvalidRequest("Plan '{}' is not in phase 2".format(planid))
    if not len(plan.routes_all.all()) < 10:
        raise InvalidRequest("No more than 10 routes can be added for a plan.")
        # raise InvalidRequest("Plan '{}' already has 10 routes".format(planid))

    event_list = list()

    for eventid in eventid_list:
        event = db_events.get_from_id(eventid, userid)
        if event.planid != plan.id:
            raise InvalidContent(
                "{} (Event '{}') does not exist in {} (Plan '{}').".format(event.name, event.id,
                                                                           plan.name, plan.planid))
            # raise InvalidContent("Event '{}' is not in Plan '{}'".format(event.id, plan.planid))
        if event not in plan.events:
            raise InvalidContent(
                "{} (Event '{}') does not have enough votes.".format(event.name, event.id))
            # raise InvalidContent("Event '{}' does not have enough votes".format(event.id))
        event_list.append(event)

    for route in plan.routes:
        if eventid_list == route.eventids:
            raise InvalidContent(
                "This route has already been suggested under the name '{}'.".format(route.name),
                content={'routeid': route.id})
            # raise InvalidContent("Event list matches Route '{}'".format(route.id), content={'routeid': route.id})

    new_route = Route(name)

    plan.routes_all.append(new_route)

    # db.session.commit()

    new_route.events += event_list

    DB.session.commit()
    return new_route


def vote(routeid, userid, vote):
    try:
        vote = int(vote)
    except ValueError:
        raise InvalidContent('Vote is not an integer')

    if not (vote >= -1 or vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    r = get_from_id(routeid, userid)
    r.vote(userid, vote)
    return r
