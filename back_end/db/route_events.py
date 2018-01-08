from back_end.db import DB


class RouteEvent(DB.Model):
    __tablename__ = 'Route_Event'
    routeid = DB.Column(DB.Integer, DB.ForeignKey('Routes.id'), primary_key=True)
    eventid = DB.Column(DB.Integer, DB.ForeignKey('Events.id'))
    index = DB.Column(DB.Integer, primary_key=True, autoincrement=True)

    def __init__(self, routeid, eventid, index):
        self.routeid = routeid
        self.eventid = eventid
        self.index = index


def get_eventids_from_routeid(routeid):
    return [x.eventid for x in RouteEvent.query.filter_by(routeid=int(routeid))]
