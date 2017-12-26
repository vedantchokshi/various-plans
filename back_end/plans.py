from datetime import datetime
from . import db

class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    eventVoteCloseDate = db.Column(db.DateTime, nullable=False)
    routeVoteCloseDate = db.Column(db.DateTime, nullable=False)
    startDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    endDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    @property
    def serialise(self):
        # TODO serialize property https://stackoverflow.com/a/7103486
        return {'name': self.name}

    def __init__(self, name, eventVoteCloseDate, routeVoteCloseDate, startDate, endDate):
        self.name = name
        self.phase = 1
        self.eventVoteCloseDate = eventVoteCloseDate
        self.routeVoteCloseDate = routeVoteCloseDate
        self.startDate = startDate
        self.endDate = endDate

def get_from_id(planid):
    try:
        return Plan.query.get(int(planid))
    except ValueError:
        return None

def create(name,eventVoteCloseDate=datetime.utcnow(), routeVoteCloseDate=datetime.utcnow(), startDate=datetime.utcnow(), endDate = datetime.utcnow()):
    newPlan = Plan(name, eventVoteCloseDate, routeVoteCloseDate, startDate, endDate)
    db.session.add(newPlan)
    db.session.commit()
    return newPlan

def countvotes(planid):
    plan = get_from_id(planid)
    plan.phase = plan.phase + 1
    db.session.commit()
    return plan
