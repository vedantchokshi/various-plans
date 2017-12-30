import events
import plans
import route_events
from back_end.api.api_exceptions import InvalidRequest, ResourceNotFound, InvalidContent
from back_end.db import db, default_str_len
from route_events import RouteEvent


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)

    plan = db.relationship('Plan', backref=db.backref('routes', lazy=True))
    events = db.relationship('Event', secondary='route_event')

    def __init__(self, name):
        self.name = name
        self.votes = 0

    def vote(self, vote):
        self.votes = self.votes + vote

    def assign_events(self, eventids):
        for i, eventid in enumerate(eventids):
            # This needs to change as self.id might not
            db.session.add(RouteEvent(self.id, eventid, i))

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['eventidList'] = [re.eventid for re in route_events.get_eventids_from_routeid(self.id).all()]
        return s


def get_from_id(routeid):
    if not str(routeid).isdigit():
        raise InvalidRequest("Route id '{}' is not a valid id".format(routeid))
    event = Route.query.get(routeid)
    if event is None:
        raise ResourceNotFound("Route not found for id '{}'".format(routeid))
    return event


def create(planid, name, eventidList):
    if name is None or not name:
        raise InvalidContent('Route name is not specified')
    if eventidList is None or len(eventidList) == 0:
        raise InvalidContent('Route event list must have a non-zero size')
    if ordered_set(eventidList) != eventidList:
        raise InvalidContent('Route cannot repeat an event')

    # Finding a plan will check the validity of planid
    plan = plans.get_from_id(planid)

    for eventid in eventidList:
        if events.get_from_id(eventid).planid != int(planid):
            raise InvalidContent("Event '{}' is not in Plan '{}'".format(eventid, planid))

    if plan.phase != 2:
        raise InvalidRequest("Plan '{}' is not in phase 2".format(planid))

    new_route = Route(name)

    plan.routes.append(new_route)

    # db.session.commit()

    # new_route.assign_events(eventids)
    for i, eventid in enumerate(eventidList):
        event = events.get_from_id(eventid)
        new_route.events.append(event)

    db.session.commit()
    return new_route


def update(routeid, vote):
    if vote is None:
        raise InvalidContent("Route vote not specified")
    if not str(vote).lstrip('-').isdigit():
        raise InvalidContent("Route vote '{}' is not a valid vote".format(vote))

    route = get_from_id(routeid)

    if route.plan.phase != 2:
        raise InvalidRequest("Plan '{}' is not in phase 2".format(route.plan.id))

    vote = int(vote)

    # TODO change this when we have user authentication
    if vote > 0:
        route.votes += 1
    if vote < 0:
        route.votes -= 1

    db.session.commit()
    return route


def ordered_set(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
