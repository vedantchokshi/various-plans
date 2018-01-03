from back_end.db import db, default_str_len
from back_end.db import routes, events

events.Event.vote = lambda self, userid, vote: _set_event_vote(self.id, userid, vote)

routes.Route.vote = lambda self, userid, vote: _set_route_vote(self.id, userid, vote)

# events.Event.votes = property(lambda self: sum(e.vote for e in self.all_votes))
events.Event.get_vote = lambda self, userid: get_event_vote(self.id, userid)

# routes.Route.votes = property(lambda self: sum(r.vote for r in self.all_votes))
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


# TODO - validate arguments
# TODO - throw errors not None?

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
    ev = EventVote.query.get((eventid, userid))
    if ev is None:
        ev = EventVote(eventid, userid, vote)
        db.session.add(ev)
    else:
        e.votes -= ev.vote
        ev.vote = vote
    e.votes += ev.vote

    db.session.commit()


def _set_route_vote(routeid, userid, vote):
    r = routes.get_from_id(routeid, userid)
    rv = RouteVote.query.get((routeid, userid))
    if rv is None:
        rv = RouteVote(routeid, userid, vote)
        db.session.add(rv)
    else:
        r.votes -= rv.vote
        rv.vote = vote
    r.votes += rv.vote

    db.session.commit()
