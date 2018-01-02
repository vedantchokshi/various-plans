from back_end.db import db, default_str_len, plans, events, route_events, authenticate_user_plan
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

    def assign_events(self, eventidList):
        for eventid in eventidList:
            event = events.get_from_id(eventid)
            self.events.append(event)

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['eventidList'] = [re.eventid for re in route_events.get_eventids_from_routeid(self.id).all()]
        return s


def get_from_id(routeid, userid):
    if not str(routeid).isdigit():
        raise InvalidRequest("Route id '{}' is not a valid id".format(routeid))
    if not authenticate_user(routeid, userid):
        raise Unauthorized('Access Denied')
    event = Route.query.get(routeid)
    if event is None:
        raise ResourceNotFound("Route not found for id '{}'".format(routeid))
    return event


def create(planid, name, eventidList, userid):
    if name is None or not name:
        raise InvalidContent('Route name is not specified')
    if eventidList is None:
        raise InvalidContent('Route eventidList is not specified')
    if len(eventidList) == 0:
        raise InvalidContent('Route eventidList must have a non-zero size')
    if len(set(eventidList)) != len(eventidList):
        raise InvalidContent('Route eventidList cannot repeat an event')

    if not authenticate_user_plan(planid, userid):
        raise Unauthorized('Access Denied')

    # Finding a plan will check the validity of planid
    plan = plans.get_from_id(planid)

    if plan.phase != 2:
        raise InvalidRequest("Plan '{}' is not in phase 2".format(planid))

    for eventid in eventidList:
        event = events.get_from_id(eventid)
        if event.planid != plan.planid:
            raise InvalidContent("Event '{}' is not in Plan '{}'".format(event.id, plan.planid))
        if event not in plan.events:
            raise InvalidContent("Event '{}' does not have enough votes".format(event.id))

    new_route = Route(name)

    plan.routes.append(new_route)

    # db.session.commit()

    new_route.assign_events(eventidList)

    db.session.commit()
    return new_route


def authenticate_user(routeid, userid):
    # AUTHTODO - get planid with routeid from route table.
    # AUTHTODO - call authenticate_user_plan(planid, userid) with the retrieved planid
    return True


def vote(routeid, userid, vote):
    return get_from_id(routeid, userid).vote(userid, vote)
