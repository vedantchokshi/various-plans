from back_end.db import db, default_str_len
from back_end.db import routes, events
from back_end.exceptions import InvalidRequest

events.Event.vote = lambda self, userid, vote: _set_event_vote(self.id, userid, vote)

routes.Route.vote = lambda self, userid, vote: _set_route_vote(self.id, userid, vote)

events.Event.votes = property(lambda self: sum(e.vote for e in self.all_votes.all()))
events.Event.get_vote = lambda self, userid: get_event_vote(self.id, userid)

routes.Route.votes = property(lambda self: sum(r.vote for r in self.all_votes.all()))
routes.Route.get_vote = lambda self, userid: get_route_vote(self.id, userid)


class EventVote(db.Model):
    __tablename__ = 'EventVote'
    eventid = db.Column(db.Integer, db.ForeignKey('Events.id'), primary_key=True)
    userid = db.Column(db.String(default_str_len), nullable=False, primary_key=True)
    vote = db.Column(db.Integer, nullable=False)

    event = db.relationship('Event', backref=db.backref('all_votes', lazy='dynamic'))

    def __init__(self, eventid, userid, vote):
        self.eventid = eventid
        self.userid = userid
        self.vote = vote

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return s


class RouteVote(db.Model):
    __tablename__ = 'RouteVote'
    routeid = db.Column(db.Integer, db.ForeignKey('Routes.id'), primary_key=True)
    userid = db.Column(db.String(default_str_len), nullable=False, primary_key=True)
    vote = db.Column(db.Integer, nullable=False)

    route = db.relationship('Route', backref=db.backref('all_votes', lazy='dynamic'))

    def __init__(self, routeid, userid, vote):
        self.routeid = routeid
        self.userid = userid
        self.vote = vote

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return s


# TODO validate arguments
# TODO throw errors not None?

def get_event_vote(eventid, userid):
    ev = EventVote.query.get((eventid, userid))
    if ev is None:
        return 0
    return ev.vote


def get_route_vote(routeid, userid):
    rv = RouteVote.query.get((routeid, userid))
    if rv is None:
        return 0
    return rv.vote


def _set_event_vote(eventid, userid, vote):
    e = events.get_from_id(eventid, userid)
    if e.plan.phase != 1:
        raise InvalidRequest("{} (Plan '{}') is not in the event voting stage, cannot vote on {} (Event '{}')".format(e.plan.name, e.plan.id, e.name, e.id))
        #raise InvalidRequest("Plan '{}' is not in phase 1, cannot vote on Event '{}'".format(e.plan.id, e.id))
    ev = EventVote.query.get((eventid, userid))
    if ev is None:
        ev = EventVote(eventid, userid, vote)
        db.session.add(ev)
    else:
        ev.vote = vote

    db.session.commit()
    e.userVoteState = e.get_vote(userid)
    return e


def _set_route_vote(routeid, userid, vote):
    r = routes.get_from_id(routeid, userid)
    if r.plan.phase != 2:
        raise InvalidRequest("{} (Plan '{}') is not in the route voting stage, cannot vote on {} (Route '{}')".format(r.plan.name, r.plan.id, r.name, r.id))
        #raise InvalidRequest("Plan '{}' is not in phase 2, cannot vote on Route '{}'".format(r.plan.id, r.id))
    rv = RouteVote.query.get((routeid, userid))
    if rv is None:
        rv = RouteVote(routeid, userid, vote)
        db.session.add(rv)
    else:
        rv.vote = vote

    db.session.commit()
    r.userVoteState = r.get_vote(userid)
    return r
