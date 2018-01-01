from back_end.db import db, default_str_len, plans, authenticate_user_plan
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent, Unauthorized


plans.Plan.events = property(
    lambda self: self.events_all.filter(Event.votes > 0) if self.phase > 1 else self.events_all)


class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('id', db.Integer, primary_key=True)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    name = db.Column(db.String(default_str_len), nullable=False)
    locationid = db.Column(db.String(default_str_len), nullable=False)

    plan = db.relationship('Plan', backref=db.backref('events_all', lazy='dynamic'))

    def __init__(self, name, locationid):
        self.name = name
        self.locationid = locationid
        self.votes = 0

    @property
    def serialise(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_from_id(eventid, userid):
    if not str(eventid).isdigit():
        raise InvalidRequest("Event id '{}' is not a valid id".format(eventid))
    if not authenticate_user(eventid, userid):
        raise Unauthorized('Access Denied')
    event = Event.query.get(eventid)
    if event is None:
        raise ResourceNotFound("Event not found for id '{}'".format(eventid))
    return event


def create(planid, name, locationid, userid):
    if name is None or not name:
        raise InvalidContent('Event name is not specified')
    if locationid is None or not locationid:
        raise InvalidContent('Event locationid is not specified')

    if not authenticate_user_plan(planid, userid):
        raise Unauthorized('Access Denied')

    plan = plans.get_from_id(planid)

    if plan.phase != 1:
        raise InvalidRequest("Plan '{}' is not in phase 1".format(planid))

    new_event = Event(name, locationid)

    plan.events.append(new_event)
    db.session.commit()
    return new_event


def authenticate_user(eventid, userid):
    # AUTHTODO - get planid with eventid from event table.
    # AUTHTODO - call authenticate_user_plan(planid, userid) with the retrieved planid
    return True