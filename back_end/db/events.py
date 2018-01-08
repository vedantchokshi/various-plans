from __future__ import print_function

from back_end.db import DB, STR_LEN, plans
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


def get_events_sql(plan):
    if plan.timephase < 2:
        return plan.events_all.all()
    if plan.timephase < 3:
        return [x for x in plan.events_all.all() if x.votes > 0]
    return plan.routes[0].events


def count_positive_events_sql(plan):
    return len([x for x in plan.events_all.all() if x.votes > 0])


plans.Plan.events = property(get_events_sql)
plans.Plan.events_count_positive = property(count_positive_events_sql)


class Event(DB.Model):
    __tablename__ = 'Events'
    id = DB.Column('id', DB.Integer, primary_key=True)
    planid = DB.Column(DB.Integer, DB.ForeignKey('Plans.id'), nullable=False)
    name = DB.Column(DB.String(STR_LEN), nullable=False)
    locationid = DB.Column(DB.String(STR_LEN), nullable=False)

    plan = DB.relationship('Plan', backref=DB.backref('events_all', lazy='dynamic'))

    def __init__(self, name, locationid):
        self.name = name
        self.locationid = locationid

    def check_user(self, userid):
        return self.plan.check_user(userid)

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['votes'] = self.votes
        s['userVoteState'] = getattr(self, 'userVoteState', False)
        return s


def get_from_id(eventid, userid):
    if not str(eventid).isdigit():
        raise InvalidRequest("Event id '{}' is not a valid id".format(eventid))
    event = Event.query.get(eventid)
    if event is None:
        raise ResourceNotFound("There is no event with the ID '{}'".format(eventid))
    event.userVoteState = event.get_vote(userid)
    return event


def create(planid, name, locationid, userid):
    if name is None or not name:
        raise InvalidContent('Please specify a name for the event.')
    if locationid is None or not locationid:
        raise InvalidContent('A location was not selected for the event')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 1:
        raise InvalidRequest(
            "You can no longer submit events to {} (Plan {})".format(plan.name, planid))
    if not len(plan.events_all.all()) < 10:
        raise InvalidRequest("No more than 10 events can be added to a plan.")

    new_event = Event(name, locationid)

    plan.events_all.append(new_event)
    DB.session.commit()
    return new_event


def vote(eventid, userid, vote):
    try:
        vote = int(vote)
    except ValueError:
        raise InvalidContent('Vote must be an integer')

    if not (vote >= -1 or vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    e = get_from_id(eventid, userid)
    e.vote(userid, vote)
    return e
