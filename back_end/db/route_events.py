from . import db

class RouteEvent(db.Model):
    __tablename__ = 'route_event'
    routeid = db.Column(db.Integer, db.ForeignKey('Routes.id'), primary_key=True)
    eventid = db.Column(db.Integer, db.ForeignKey('Events.id'), primary_key=True)
    index = db.Column(db.Integer, primary_key=True, nullable=False)

    def __init__(self, routeid, eventid, index):
        self.routeid = routeid
        self.eventid = eventid
        self.index = index

    @property
    def serialise(self):
        # TODO serialize property https://stackoverflow.com/a/7103486
        return {'name': self.name}
