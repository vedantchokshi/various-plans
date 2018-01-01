import time

from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent, Unauthorized
from back_end.db import db, default_str_len
from back_end.db import authenticate_user_plan


class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    eventVoteCloseTime = db.Column(db.Integer, nullable=False)
    routeVoteCloseTime = db.Column(db.Integer, nullable=False)
    startTime = db.Column(db.Integer, nullable=False)
    endTime = db.Column(db.Integer, nullable=False)
    join_link = db.Column(db.String(default_str_len), nullable=False)
    ownerid = db.Column(db.String(default_str_len), nullable=False)

    def __init__(self, name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime):
        self.name = name
        self.eventVoteCloseTime = eventVoteCloseTime
        self.routeVoteCloseTime = routeVoteCloseTime
        self.startTime = startTime
        self.endTime = endTime

    @property
    def phase(self):
        now = int(time.time())
        if now < self.eventVoteCloseTime:
            return 1
        if now < self.routeVoteCloseTime:
            return 2
        return 3

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['phase'] = self.phase
        return s


def get_from_id(planid, userid):
    # TODO change when planid is alphanumeric hash
    if planid is None:
        raise InvalidRequest('Plan id not specified')
    if not str(planid).isdigit():
        raise InvalidRequest('Plan id \'{}\' is not a valid id'.format(planid))
    if not authenticate_user_plan(planid, userid):
        raise Unauthorized('Access Denied')
    plan = Plan.query.get(planid)
    if plan is None:
        raise ResourceNotFound('Plan not found for id \'{}\''.format(planid))
    return plan


# If keys are not in json, function will be given None, therefore needs to cope with such value
# Nones here are in order to use default values
def create(name, eventVoteCloseTime=None, routeVoteCloseTime=None, endTime=None, userid):
    if name is None or not name:
        # name is not specified in json or is the empty string
        raise InvalidContent("Plan name not specified")
    # TODO split number check with different error
    if eventVoteCloseTime is None or not str(eventVoteCloseTime).isdigit():
        raise InvalidContent("Plan eventVoteCloseTime not specified")
    if routeVoteCloseTime is None or not str(routeVoteCloseTime).isdigit():
        raise InvalidContent("Plan routeVoteCloseTime not specified")
    # if startTime is None or not str(startTime).isdigit():
    #     raise InvalidContent("Plan startTime not specified")
    if endTime is None or not str(endTime).isdigit():
        raise InvalidContent("Plan endTime not specified")

    startTime = int(time.time())

    # AUTHTODO - Generate a hash ( import os; import binascii, planhash=binascii.hexlify(os.urandom(16)) )
    # store hash in the the plan table (plan.joinid) and we MUST send the hash back to the client.
    # AUTHTODO - assign the userid as the plan.owner of the plan in the plan table.

    new_plan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)

    # The following isn't used as pymysql doesn't complain if name = "",
    #   better to check argument before making plan
    # try:
    #     new_plan = Plan(name, eventVoteCloseTime, routeVoteCloseTime, startTime, endTime)
    # except IntegrityError as e:
    #     raise InvalidInput, InvalidInput(e.message),

    db.session.add(new_plan)
    db.session.commit()
    return new_plan

