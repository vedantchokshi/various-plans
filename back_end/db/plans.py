import binascii
import os
import time

from back_end.db import db, default_str_len
from back_end.db.plan_users import PlanUser
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent, Unauthorized

# length needs to be even, otherwise will be rounded down
joinid_length = 8


class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(default_str_len), nullable=False)
    eventVoteCloseTime = db.Column(db.Integer, nullable=False)
    routeVoteCloseTime = db.Column(db.Integer, nullable=False)
    startTime = db.Column(db.Integer, nullable=False)
    endTime = db.Column(db.Integer, nullable=False)
    joinid = db.Column(db.String(default_str_len), nullable=False)
    ownerid = db.Column(db.String(default_str_len), nullable=False)

    def __init__(self, name, event_vote_close_time, route_vote_close_time, start_time, end_time, ownerid):
        self.name = name
        self.eventVoteCloseTime = event_vote_close_time
        self.routeVoteCloseTime = route_vote_close_time
        self.startTime = start_time
        self.endTime = end_time
        self.ownerid = ownerid
        self.users.append(PlanUser(self.id, ownerid))
        self.joinid = binascii.hexlify(os.urandom(joinid_length / 2))

    def check_user(self, userid):
        return userid in [u.userid for u in self.users]

    @property
    def timephase(self):
        now = int(time.time())
        if now < self.eventVoteCloseTime:
            return 1
        if now < self.routeVoteCloseTime:
            return 2
        if now < self.endTime:
            return 3
        return 4

    @property
    def phase(self):
        # p = self.timephase
        # if p > 1 and len(self.events) == 0:
        #     return 4
        # if p > 2 and len(self.routes) == 0:
        #     return 4
        # return p
        return self.timephase

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['phase'] = self.phase
        return s


def get_from_id(planid, userid):
    if planid is None:
        raise InvalidRequest('Plan id not specified')
    if not str(planid).isdigit():
        raise InvalidRequest("Plan id '{}' is not a valid id".format(planid))
    plan = Plan.query.get(planid)
    if plan is None:
        raise ResourceNotFound("Plan not found for id '{}'".format(planid))
    if not plan.check_user(userid):
        raise Unauthorized("User not authorized for Plan '{}'".format(planid))
    return plan


def create(name, event_vote_close_time, route_vote_close_time, end_time, userid):
    if name is None or not name:
        # name is not specified in json or is the empty string
        raise InvalidContent("Plan name not specified")
    # TODO split number check with different error
    if event_vote_close_time is None or not str(event_vote_close_time).isdigit():
        raise InvalidContent("Plan eventVoteCloseTime not specified")
    if route_vote_close_time is None or not str(route_vote_close_time).isdigit():
        raise InvalidContent("Plan routeVoteCloseTime not specified")
    # if startTime is None or not str(startTime).isdigit():
    #     raise InvalidContent("Plan startTime not specified")
    if end_time is None or not str(end_time).isdigit():
        raise InvalidContent("Plan endTime not specified")

    startTime = int(time.time())

    new_plan = Plan(name, event_vote_close_time, route_vote_close_time, startTime, end_time, userid)

    db.session.add(new_plan)
    db.session.commit()
    return new_plan


def get_events_from_id(planid, userid):
    events = get_from_id(planid, userid).events
    for event in events:
        event.userVoteState = event.get_vote(userid)
    return events


def get_routes_from_id(planid, userid):
    plan = get_from_id(planid, userid)
    routes = plan.routes
    for route in routes:
        route.userVoteState = route.get_vote(userid)
    return routes


def add_user(joinid, userid):
    plans = Plan.query.filter_by(joinid=joinid).all()
    if (len(plans) < 1) or None :
        raise ResourceNotFound("Cannot find Plan for joinid '{}'".format(joinid))
    plan = plans[0]
    if userid not in [pu.userid for pu in plan.users]:
        plan.users.append(PlanUser(plan.id, userid))
        db.session.commit()
    return plan
