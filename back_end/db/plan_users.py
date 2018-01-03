from back_end.db import db, default_str_len


class PlanUser(db.Model):
    __tablename__ = 'Plan_Users'
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), primary_key=True)
    userid = db.Column(db.String(default_str_len), primary_key=True)

    plan = db.relationship('Plan', backref=db.backref('users', lazy=True))

    def __init__(self, planid, userid):
        self.planid = planid
        self.userid = userid


def get_plans(userid):
    plans = PlanUser.query.filterby(userid=userid)
    return [p.plan for p in plans]
