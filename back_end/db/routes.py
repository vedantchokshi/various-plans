from back_end.db import db, default_str_len, plans, events as db_events
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent, BaseApiException


def get_routes(self):
    if self.phase <= 2:
        rs = self.routes_all.all()
        return sort_routes(rs) if len(rs) > 0 else []
    if self.phase >= 3:
        r = self.routes_all.all()
        if len(r) > 0:
            r = sort_routes(r)[-1]
            return [r]
        else:
            return []


def sort_routes(route_list):
    def sorter(a, b):
        if not isinstance(a, Route) or not isinstance(b, Route):
            raise BaseApiException('Routes list does not contain route objects', 500)
        if a.votes != b.votes:
            # Highest total votes
            return cmp(b.votes, a.votes)
        a_event_average = sum([e.votes for e in a.events], 0.0) / len(a.events)
        b_event_average = sum([e.votes for e in b.events], 0.0) / len(b.events)
        if a_event_average != b_event_average:
            # Highest average event total votes
            return cmp(b_event_average, a_event_average)
        if len(a.events) != len(b.events):
            # Highest number of events
            return cmp(len(b.events), len(a.events))
        a_downvotes = reduce(lambda x, y: x + (1 if y.vote < 1 else 0), a.all_votes.all())
        b_downvotes = reduce(lambda x, y: x + (1 if y.vote < 1 else 0), b.all_votes.all())
        if a_downvotes != b_downvotes:
            # Least down-voted route
            return cmp(a_downvotes, b_downvotes)
        return cmp(a.id, b.id)

    return sorted(route_list, cmp=sorter)


plans.Plan.routes = property(get_routes)


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    # votes = db.Column(db.Integer, nullable=False)

    plan = db.relationship('Plan', backref=db.backref('routes_all', lazy='dynamic'))
    events = db.relationship('Event', secondary='Route_Event')

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
        if event.planid != plan.id:
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
    except ValueError:
        raise InvalidContent('Vote is not an integer')

    if not (vote >= -1 or vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    r = get_from_id(routeid, userid)
    r.vote(userid, vote)
    return r
