"""
Event object for working with database and event functions for API
"""
from back_end.db import DB, STR_LEN, plans
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


def get_events(plan):
    """
    Get all the events associated with this plan.
    This list is filtered to all positively voted events if the plan
    is in phase 2 and to only the events in the winning route in phase 3.
    """
    if plan.timephase < 2:
        return plan.events_all.all()
    if plan.timephase < 3:
        return [x for x in plan.events_all.all() if x.votes > 0]
    return plan.routes[0].events if plan.routes else []


def count_positive_events(plan):
    """
    Get a count of all positively voted events associated with this plan.
    """
    return len([x for x in plan.events_all.all() if x.votes > 0])


plans.Plan.events = property(get_events)
plans.Plan.events_count_positive = property(count_positive_events)


class Event(DB.Model):
    """
    Event object that represents an entry in the 'Events' table
    """
    __tablename__ = 'Events'
    id = DB.Column('id', DB.Integer, primary_key=True)
    planid = DB.Column(DB.Integer, DB.ForeignKey('Plans.id'), nullable=False)
    name = DB.Column(DB.String(STR_LEN), nullable=False)
    locationid = DB.Column(DB.String(STR_LEN), nullable=False)

    plan = DB.relationship('Plan', backref=DB.backref('events_all', lazy='dynamic'))

    def __init__(self, name, locationid):
        self.name = name
        self.locationid = locationid

    def check_user(self, userid):
        """
        Check if a user is allowed to access the event's plan

        :param str userid: Google auth user ID
        """
        return self.plan.check_user(userid)

    @property
    def serialise(self):
        """
        Used to create a dictionary for jsonifying

        :return: dictionary representation of Event object
        """
        result = dict()
        result['id'] = self.id
        result['name'] = self.name
        result['locationid'] = self.locationid
        result['planid'] = self.planid
        result['votes'] = self.votes
        result['userVoteState'] = getattr(self, 'userVoteState', False)
        return result


def get_from_id(eventid, userid):
    """
    Get an event object from an ID
    """
    if not str(eventid).isdigit():
        raise InvalidRequest("Event id '{}' is not a valid id".format(eventid))
    event = Event.query.get(eventid)
    if event is None:
        raise ResourceNotFound("There is no event with the ID '{}'".format(eventid))
    event.check_user(userid)
    event.userVoteState = event.get_vote(userid)
    return event


def create(planid, name, locationid, userid):
    """
    Create an event object with input validation and commit the object to the database
    """
    if name is None or not name:
        raise InvalidContent('Please specify a name for the event')
    if locationid is None or not locationid:
        raise InvalidContent('A location was not selected for the event')

    plan = plans.get_from_id(planid, userid)

    if plan.timephase != 1:
        raise InvalidRequest(
            "You can no longer submit events to {} (Plan {})".format(plan.name, planid))
    if not len(plan.events_all.all()) < 10:
        raise InvalidRequest("No more than 10 events can be added to a plan")

    new_event = Event(name, locationid)

    plan.events_all.append(new_event)
    DB.session.commit()
    return new_event


def vote(eventid, userid, submitted_vote):
    """
    Add a vote from a user to an event
    """
    try:
        submitted_vote = int(submitted_vote)
    except ValueError:
        raise InvalidContent('Vote must be an integer')

    if not (submitted_vote >= -1 or submitted_vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    return get_from_id(eventid, userid).vote(userid, submitted_vote)
