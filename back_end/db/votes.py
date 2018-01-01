from back_end.db import routes, events
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent
from back_end.db import db, default_str_len


events.Event.vote = 
    lambda self, userid, vote: _set_event_vote(self.id, userid, vote)

routes.Route.vote =
    lambda self, userid, vote: _set_route_vote(self.id, userid, vote)

events.Event.vote_count = property(
    lambda self: sum(e.vote for e in EventVote.query.filter_by(eventid=self.id)))

routes.Route.vote_count = property(
    lambda self: sum(r.vote for r in RouteVote.query.filter_by(routeid=self.id)))


class EventVote(db.Model):
    __tablename__ = 'EventVote'
    eventid = db.Column(db.Integer, db.ForeignKey('Events.id'), primary_key=True)
    userid = db.Column(db.String(default_str_len), nullable=False, primary_key=True)
    vote = db.Column(db.Integer, nullable=False)

    event = db.relationship('Event', backref=db.backref('votes', lazy='dynamic'))

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

    route = db.relationship('Route', backref=db.backref('votes', lazy='dynamic'))

    def __init__(self, routeid, userid, vote):
        self.routeid = routeid
        self.userid = userid
        self.vote = vote

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return s


def get_event_votes(userid):
    try:
        return EventVote.query.filter_by(userid=userid)
    except ValueError:
        return None

def get_route_votes(userid):
        try:
            return RouteVote.query.filter_by(userid=userid)
        except ValueError:
            return None

def _set_event_vote(eventid, userid, vote):
    try:
        ev = EventVote.query.filter_by(eventid=int(eventid), userid=userid)
        if not ev:
            ev = EventVote(eventid, userid, vote)
            db.session.add(ev)
        else:
            ev.vote = vote

        db.session.commit()
    except ValueError:
        return None

def _set_route_vote(routeid, userid, vote):
        try:
            rv = RouteVote.query.filter_by(routeid=int(routeid), userid=userid)
        if not rv:
            rv = RouteVote(routeid, userid, vote)
            db.session.add(rv)
        else:
            rv.vote = vote

        db.session.commit()
    except ValueError:
        return None

