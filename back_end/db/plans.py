import time
from . import db

class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    eventVoteCloseTime = db.Column(db.Float, nullable=False)
    routeVoteCloseTime = db.Column(db.Float, nullable=False)
    startTime = db.Column(db.Float, nullable=False)
    endTime = db.Column(db.Float, nullable=False)


    def __init__(self, name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime):
        self.name = name
        self.phase = 1
        self.eventVoteCloseTime = eventVoteCloseTime
        self.routeVoteCloseTime = routeVoteCloseTime
        self.startTime = startTime
        self.endTime = endTime

    @property
    def serialise(self):
        # TODO serialize property https://stackoverflow.com/a/7103486
        return {'name': self.name}

def get_from_id(planid):
    try:
        return Plan.query.get(int(planid))
    except ValueError:
        return None

# TODO remove defaults for vote Times
def create(name, eventVoteCloseTime=time.time(), routeVoteCloseTime=time.time(),
           startTime=time.time(), endTime=time.time()):
    newPlan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)
    db.session.add(newPlan)
    db.session.commit()
    return newPlan


def countvotes(planid):
    plan = get_from_id(planid)
    plan.phase = plan.phase + 1
    db.session.commit()
    return plan
