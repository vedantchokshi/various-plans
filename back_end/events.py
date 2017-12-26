from . import db, jsonify_decorator
import plans
from flask import Blueprint, request

ROUTES = Blueprint('events', __name__)

# TODO add exceptions to Blueprint or app

class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('id', db.Integer, primary_key=True)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float, default=0, nullable=False)
    latitude = db.Column(db.Float, default=0, nullable=False)
    votes = db.Column(db.Integer, default=0, nullable=False)

    plan = db.relationship('Plan', backref=db.backref('events', lazy=True))

    @property
    def serialise(self):
        # TODO serialize property https://stackoverflow.com/a/7103486
        return {'name': self.name}

    def __init__(self, name, location, longitude, latitude):
        self.name = name
        self.location = location
        self.votes = 0
        self.longitude = longitude
        self.latitude = latitude

    def vote(self, vote):
        self.votes = self.votes + vote

@ROUTES.route('/id/<id>', methods=['GET'])
@jsonify_decorator
def get_from_id(id):
    try:
        return Event.query.get(id)
    except ValueError:
        # TODO input validation
        # TODO useful exceptions
        return None

def create(planid, name, location, longitude=0, latitude=0):
    plan = plans.get_from_id(planid)
    if plan.phase !=1:
        return None

    e = Event(name, location, longitude, latitude)
    plan.events.append(e)
    db.session.commit()
    return e

def upvote(eventid):
    e = get_from_id(eventid)
    e.votes = e.votes + 1
    db.session.commit()
    return e

def downvote(eventid):
    e = get_from_id(eventid)
    e.votes = e.votes - 1
    db.session.commit()
    return e
