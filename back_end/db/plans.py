import time
from . import db, default_str_len


# TODO remove end time

class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_from_id(planid):
    plan = Plan.query.get(int(planid))
    if plan is None:
        # TODO raise not found exception
        pass
    return plan


# TODO remove defaults for vote times
# If keys are not in json, function will be given None, therefore needs to cope with such value
def create(name, eventVoteCloseTime=None, routeVoteCloseTime=None, startTime=None, endTime=None):
    if name is None:
        # TODO raise argument error
        pass
    if eventVoteCloseTime is None:
        eventVoteCloseTime = time.time()
    if routeVoteCloseTime is None:
        routeVoteCloseTime = time.time()
    if startTime is None:
        startTime = time.time()
    if endTime is None:
        endTime = time.time()

    # TODO does this complain if name = None?
    newPlan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)
    db.session.add(newPlan)
    db.session.commit()
    return newPlan


def countvotes(planid):
    plan = get_from_id(planid)
    plan.phase = plan.phase + 1
    db.session.commit()
    return plan
