"""
EventVote and RouteVote objects and voting functions for other models
"""
from back_end.db import DB, STR_LEN
from back_end.db import routes, events
from back_end.exceptions import InvalidRequest

events.Event.vote = lambda self, userid, vote: _set_event_vote(self.id, userid, vote)

routes.Route.vote = lambda self, userid, vote: _set_route_vote(self.id, userid, vote)

events.Event.votes = property(lambda self: sum(e.vote for e in self.all_votes.all()))
events.Event.get_vote = lambda self, userid: get_event_vote(self.id, userid)

routes.Route.votes = property(lambda self: sum(r.vote for r in self.all_votes.all()))
routes.Route.get_vote = lambda self, userid: get_route_vote(self.id, userid)


class EventVote(DB.Model):
    # pylint: disable-msg=too-few-public-methods
    """
    EventVote object that records how a user voted on an event
    """
    __tablename__ = 'EventVote'
    eventid = DB.Column(DB.Integer, DB.ForeignKey('Events.id'), primary_key=True)
    userid = DB.Column(DB.String(STR_LEN), nullable=False, primary_key=True)
    vote = DB.Column(DB.Integer, nullable=False)

    event = DB.relationship('Event', backref=DB.backref('all_votes', lazy='dynamic'))

    def __init__(self, eventid, userid, vote):
        self.eventid = eventid
        self.userid = userid
        self.vote = vote

    @property
    def serialise(self):
        """
        Used to create a dictionary for jsonifying

        :return: dictionary representation of EventVote object
        """
        result = dict()
        result['eventid'] = self.eventid
        result['userid'] = self.userid
        result['vote'] = self.vote
        return result


class RouteVote(DB.Model):
    # pylint: disable-msg=too-few-public-methods
    """
    RouteVote object that records how a user voted on a route
    """
    __tablename__ = 'RouteVote'
    routeid = DB.Column(DB.Integer, DB.ForeignKey('Routes.id'), primary_key=True)
    userid = DB.Column(DB.String(STR_LEN), nullable=False, primary_key=True)
    vote = DB.Column(DB.Integer, nullable=False)

    route = DB.relationship('Route', backref=DB.backref('all_votes', lazy='dynamic'))

    def __init__(self, routeid, userid, vote):
        self.routeid = routeid
        self.userid = userid
        self.vote = vote

    @property
    def serialise(self):
        """
        Used to create a dictionary for jsonifying

        :return: dictionary representation of RouteVote object
        """
        result = dict()
        result['routeid'] = self.routeid
        result['userid'] = self.userid
        result['vote'] = self.vote
        return result


def get_event_vote(eventid, userid):
    """
    Get how a user voted on an event
    """
    event_vote = EventVote.query.get((eventid, userid))
    if event_vote is None:
        return 0
    return event_vote.vote


def get_route_vote(routeid, userid):
    """
    Get how a user voted on a route
    """
    route_vote = RouteVote.query.get((routeid, userid))
    if route_vote is None:
        return 0
    return route_vote.vote


def _set_event_vote(eventid, userid, vote):
    event = events.get_from_id(eventid, userid)
    if event.plan.phase != 1:
        raise InvalidRequest(
            "{} (Plan '{}') is not in the event voting stage, cannot vote on {} (Event '{}')"
            .format(event.plan.name, event.plan.id, event.name, event.id))
    event_vote = EventVote.query.get((eventid, userid))
    if event_vote is None:
        event_vote = EventVote(eventid, userid, vote)
        DB.session.add(event_vote)
    else:
        event_vote.vote = vote

    DB.session.commit()
    event.userVoteState = event.get_vote(userid)
    return event


def _set_route_vote(routeid, userid, vote):
    route = routes.get_from_id(routeid, userid)
    if route.plan.phase != 2:
        raise InvalidRequest(
            "{} (Plan '{}') is not in the route voting stage, cannot vote on {} (Route '{}')"
            .format(route.plan.name, route.plan.id, route.name, route.id))
    route_vote = RouteVote.query.get((routeid, userid))
    if route_vote is None:
        route_vote = RouteVote(routeid, userid, vote)
        DB.session.add(route_vote)
    else:
        route_vote.vote = vote

    DB.session.commit()
    route.userVoteState = route.get_vote(userid)
    return route
