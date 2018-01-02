from back_end.db import db


class RouteEvent(db.Model):
    __tablename__ = 'Route_Event'
    routeid = db.Column(db.Integer, db.ForeignKey('Routes.id'), primary_key=True)
    eventid = db.Column(db.Integer, db.ForeignKey('Events.id'))
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __init__(self, routeid, eventid, index):
        self.routeid = routeid
        self.eventid = eventid
        self.index = index


def get_eventids_from_routeid(routeid):
    return RouteEvent.query.filter_by(routeid=int(routeid))
