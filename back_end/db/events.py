from __future__ import print_function

from back_end.db import db, default_str_len, plans
from back_end.exceptions import InvalidRequest, ResourceNotFound, InvalidContent


# def get_events(plan):
#     events = plan.events_all.all()
#     if len(events) > 0:
#         # Sort events based on our criteria
#         # events = sort_events(events)
#         if plan.timephase < 2:
#             # Phase 1 requires no filtering of events
#             return events
#         # Phases 2, 3, 4 require positively voted events
#         events = [event for event in events if event.votes > 0]
#         if plan.timephase < 3:
#             # Phase 2 requires no more filtering of events
#             return events
#         # Phases 3 and 4 require only events from winning route
#         routes = plan.routes
#         if len(routes) > 0:
#             # Filter events if there is a winning route
#             route = routes[0]
#             route_event_ids = [event.id for event in route.events]
#             events = [event for event in events if event.id in route_event_ids]
#             return events
#     return []
#
#
# def sort_events(event_list):
#     def sorter(a, b):
#         if not isinstance(a, Event) or not isinstance(b, Event):
#             raise BaseApiException('Routes list does not contain route objects', 500)
#         if a.votes != b.votes:
#             # Highest total votes
#             return cmp(b.votes, a.votes)
#         a_downvotes = reduce(lambda x, y: x + (1 if y.vote < 1 else 0), a.all_votes.all(), 0)
#         b_downvotes = reduce(lambda x, y: x + (1 if y.vote < 1 else 0), b.all_votes.all(), 0)
#         if a_downvotes != b_downvotes:
#             # Least down-voted route
#             return cmp(a_downvotes, b_downvotes)
#         # Order of creation
#         return cmp(a.id, b.id)
#
#     return sorted(event_list, cmp=sorter)


def get_events_sql(plan):
    if plan.timephase < 2:
        return plan.events_all.all()
    return plan.events_all.filter(Event.votes > 0).all()


def count_positive_events_sql(plan):
    return plan.events_all.filter(Event.votes > 0).count()


plans.Plan.events = property(get_events_sql)
plans.Plan.events_count_positive = property(count_positive_events_sql)


class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('id', db.Integer, primary_key=True)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    name = db.Column(db.String(default_str_len), nullable=False)
    locationid = db.Column(db.String(default_str_len), nullable=False)
    # votes = db.Column(db.Integer, nullable=False)

    plan = db.relationship('Plan', backref=db.backref('events_all', lazy='dynamic'))

    def __init__(self, name, locationid):
        self.name = name
        self.locationid = locationid

    def check_user(self, userid):
        return self.plan.check_user(userid)

    @property
    def serialise(self):
        s = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        s['votes'] = self.votes
        s['userVoteState'] = getattr(self, 'userVoteState', False)
        return s


def get_from_id(eventid, userid):
    if not str(eventid).isdigit():
        raise InvalidRequest("Event id '{}' is not a valid id".format(eventid))
    event = Event.query.get(eventid)
    if event is None:
        raise ResourceNotFound("There is no event with the ID '{}'".format(eventid))
        #raise ResourceNotFound("Event not found for id '{}'".format(eventid))
    event.userVoteState = event.get_vote(userid)
    return event


def create(planid, name, locationid, userid):
    if name is None or not name:
        raise InvalidContent('Please specify a name for the event.')
        #raise InvalidContent('Event name is not specified')
    if locationid is None or not locationid:
        raise InvalidContent('A location was not selected for the event')
        #raise InvalidContent('Event locationid is not specified')

    plan = plans.get_from_id(planid, userid)

    if plan.phase != 1:
        raise InvalidRequest("You can no longer submit events to {} (Plan {})".format(plan.name,planid))
        #raise InvalidRequest("Plan '{}' is not in phase 1".format(planid))
    if not len(plan.events_all.all()) < 10:
        raise InvalidRequest("No more than 10 events can be added for a plan.")
        #raise InvalidRequest("Plan '{}' already has 10 events".format(planid))

    new_event = Event(name, locationid)

    plan.events_all.append(new_event)
    db.session.commit()
    return new_event


def vote(eventid, userid, vote):
    try:
        vote = int(vote)
    except ValueError:
        raise InvalidContent('Vote must be an integer')

    if not (vote >= -1 or vote <= 1):
        raise InvalidContent('Vote must be -1, 0 or 1')
    e = get_from_id(eventid, userid)
    e.vote(userid, vote)
    return e
