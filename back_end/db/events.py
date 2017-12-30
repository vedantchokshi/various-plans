import plans
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent
from back_end.db import db, default_str_len


class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('id', db.Integer, primary_key=True)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    name = db.Column(db.String(default_str_len), nullable=False)
    locationid = db.Column(db.String(default_str_len), nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)

    plan = db.relationship('Plan', backref=db.backref('events', lazy=True))

    def __init__(self, name, locationid):
        self.name = name
        self.locationid = locationid
        self.votes = 0

    def vote(self, vote):
        self.votes = self.votes + vote

    @property
    def serialise(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_from_id(eventid):
    if not str(eventid).isdigit():
        raise InvalidRequest("Event id '{}' is not a valid id".format(eventid))
    event = Event.query.get(eventid)
    if event is None:
        raise ResourceNotFound("Event not found for id '{}'".format(eventid))
    return event


def create(planid, name, locationid):
    if name is None or not name:
        raise InvalidContent('Event name is not specified')
    if locationid is None or not locationid:
        raise InvalidContent('Event locationid is not specified')

    plan = plans.get_from_id(planid)

    if plan.phase != 1:
        raise InvalidRequest("Plan '{}' is not in phase 1".format(planid))

    new_event = Event(name, locationid)

    plan.events.append(new_event)
    db.session.commit()
    return new_event


def update(eventid, vote):
    if vote is None:
        raise InvalidContent("Event vote not specified")
    if not str(vote).lstrip('-').isdigit():
        raise InvalidContent("Event vote '{}' is not a valid vote".format(vote))

    event = get_from_id(eventid)

    if event.plan.phase != 1:
        raise InvalidRequest("Plan '{}' is not in phase 1".format(event.plan.id))

    vote = int(vote)

    # TODO change this when we have user authentication
    if vote > 0:
        event.votes += 1
    if vote < 0:
        event.votes -= 1

    db.session.commit()
    return event
