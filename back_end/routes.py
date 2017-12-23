from . import db
from route_events import RouteEvent
import plans

class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)

    plan = db.relationship('Plan', backref=db.backref('routes', lazy=True))
    events = db.relationship("Event", secondary='route_event')

    def __init__(self, name):
        self.name = name
        self.votes = 0

    def vote(self, vote):
        self.votes = self.votes + vote

    def assignEvents(self, eventids):
        for i, eventid in enumerate(eventids):
            db.session.add(RouteEvent(self.id, eventid, i))

def get_from_id(routeid):
    try:
        return Route.query.get(routeid)
    except ValueError:
            return None

def create(planid, name, events):
    plan = plans.get_from_id(planid)
    # TODO check plan in phase 2
    r = Route(name)
    plan.routes.append(r)
    db.session.commit()

    # TODO check events are valid for plan
    r.assignEvents(list(map(int, events.split(','))))
    db.session.commit()
    return r

def upvote(routeid):
    r = get_from_id(routeid)
    r.votes = r.votes + 1
    db.session.commit()
    return r

def downvote(routeid):
    r = get_from_id(routeid)
    r.votes = r.votes - 1
    db.session.commit()
    return r
