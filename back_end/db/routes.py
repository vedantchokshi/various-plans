from back_end.db import db, default_str_len, plans, events, route_events
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent, Unauthorized

plans.Plan.routes = property(
    lambda self: self.routes_all.order_by(Route.votes.desc())[0:1] if self.phase > 2 else self.routes_all)


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)

    plan = db.relationship('Plan', backref=db.backref('routes_all', lazy='dynamic'))
    events = db.relationship('Event', secondary='Route_Event')

    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.userVoteState = None

    def assign_events(self, eventidList, userid):
        for eventid in eventidList:
            event = events.get_from_id(eventid, userid)
            self.events.append(event)

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['eventidList'] = [re.eventid for re in route_events.get_eventids_from_routeid(self.id).all()]
        s['userVoteState'] = getattr(self, 'userVoteState')
        return s


def get_from_id(routeid, userid):
    if not str(routeid).isdigit():
        raise InvalidRequest("Route id '{}' is not a valid id".format(routeid))
    route = Route.query.get(routeid)
    if route is None:
        raise ResourceNotFound("Route not found for id '{}'".format(routeid))
    route.userVoteState = route.get_vote(userid)
    return route


def create(planid, name, eventidList, userid):
    if name is None or not name:
        raise InvalidContent('Route name is not specified')
    if eventidList is None:
        raise InvalidContent('Route eventidList is not specified')
    if len(eventidList) == 0:
        raise InvalidContent('Route eventidList must have a non-zero size')
    if len(set(eventidList)) != len(eventidList):
        raise InvalidContent('Route eventidList cannot repeat an event')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 2:
        raise InvalidRequest("Plan '{}' is not in phase 2".format(planid))

    for eventid in eventidList:
        event = events.get_from_id(eventid, userid)
        if event.planid != plan.planid:
            raise InvalidContent("Event '{}' is not in Plan '{}'".format(event.id, plan.planid))
        if event not in plan.events:
            raise InvalidContent("Event '{}' does not have enough votes".format(event.id))

    new_route = Route(name)

    plan.routes.append(new_route)

    # db.session.commit()

    new_route.assign_events(eventidList, userid)

    db.session.commit()
    return new_route


def vote(routeid, userid, vote):
    if not str(vote).isdigit():
        raise InvalidContent('Vote is not an integer')
    vote = int(vote)
    if vote < -1 or vote > 1:
        raise InvalidContent('Vote must be -1, 0 or 1')
    return get_from_id(routeid, userid).vote(userid, vote)
