import random

from back_end.db import db, default_str_len, plans, events as db_events, route_events
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


def get_best_route(self):
    if self.phase > 2:
        r = self.routes_all.order_by(Route.votes.desc())[0]
        r_list = self.routes_all.filter_by(votes=r.votes).all()
        if len(r_list) > 1:
            i = random.randint(0, len(r_list))
            r = r_list[i]
            r.votes += 1
            db.session.commit()
        return list(r)
    else:
        return self.routes_all.all()


plans.Plan.routes = property(get_best_route)


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False)

    plan = db.relationship('Plan', backref=db.backref('routes_all', lazy='dynamic'))
    events = db.relationship('Event', secondary='Route_Event')

    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.userVoteState = None

    @property
    def eventids(self):
        return [re.eventid for re in route_events.get_eventids_from_routeid(self.id).all()]

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['eventidList'] = self.eventids
        s['userVoteState'] = getattr(self, 'userVoteState', False)
        return s


def get_from_id(routeid, userid):
    if not str(routeid).isdigit():
        raise InvalidRequest("Route id '{}' is not a valid id".format(routeid))
    route = Route.query.get(routeid)
    if route is None:
        raise ResourceNotFound("Route not found for id '{}'".format(routeid))
    route.userVoteState = route.get_vote(userid)
    return route


def create(planid, name, eventid_list, userid):
    if name is None or not name:
        raise InvalidContent('Route name is not specified')
    if eventid_list is None:
        raise InvalidContent('Route eventidList is not specified')
    if len(eventid_list) == 0:
        raise InvalidContent('Route eventidList must have a non-zero size')
    if len(set(eventid_list)) != len(eventid_list):
        raise InvalidContent('Route eventidList cannot repeat an event')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 2:
        raise InvalidRequest("Plan '{}' is not in phase 2".format(planid))

    event_list = list()

    for eventid in eventid_list:
        event = db_events.get_from_id(eventid, userid)
        if event.planid != plan.planid:
            raise InvalidContent("Event '{}' is not in Plan '{}'".format(event.id, plan.planid))
        if event not in plan.events:
            raise InvalidContent("Event '{}' does not have enough votes".format(event.id))
        event_list.append(event)

    for route in plan.routes:
        if eventid_list == route.eventids:
            raise InvalidContent("Event list matches Route '{}'".format(route.id), content={'routeid': route.id})

    new_route = Route(name)

    plan.routes_all.append(new_route)

    # db.session.commit()

    new_route.events += event_list

    db.session.commit()
    return new_route


def vote(routeid, userid, vote):
    try:
        vote = int(vote)
    except ValueError :
        raise InvalidContent('Vote is not an integer')

    if not (vote >= -1 or vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    r = get_from_id(routeid, userid)
    r.vote(userid, vote)
    return r
