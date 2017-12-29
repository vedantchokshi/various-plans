import time

from back_end.api.api_exceptions import InvalidRequest, ResourceNotFound, InvalidContent
from back_end.db import db, default_str_len


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
    # TODO change when planid is alphanumeric hash
    if not str(planid).isdigit():
        raise InvalidRequest('Plan id \'{}\' is not a valid id'.format(planid))
    plan = Plan.query.get(planid)
    if plan is None:
        raise ResourceNotFound('Plan not found for id \'{}\''.format(planid))
    return plan


# If keys are not in json, function will be given None, therefore needs to cope with such value
# Nones here are in order to use default values
def create(name, eventVoteCloseTime=None, routeVoteCloseTime=None, startTime=None, endTime=None):
    if name is None or not name:
        # name is not specified in json or is the empty string
        raise InvalidContent("Plan name not specified")

    # TODO remove defaults for vote times, replace with raising InvalidInput
    if eventVoteCloseTime is None:
        eventVoteCloseTime = time.time()
    if routeVoteCloseTime is None:
        routeVoteCloseTime = time.time()
    if startTime is None:
        startTime = time.time()
    if endTime is None:
        endTime = time.time()

    newPlan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)

    # The following isn't used as pymysql doesn't complain if name = "",
    #   better to check argument before making plan
    # try:
    #     newPlan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)
    # except IntegrityError as e:
    #     raise InvalidInput, InvalidInput(e.message),

    db.session.add(newPlan)
    db.session.commit()
    return newPlan


# TODO remove as phase isn't needed
def countvotes(planid):
    plan = get_from_id(planid)
    plan.phase = plan.phase + 1
    db.session.commit()
    return plan
