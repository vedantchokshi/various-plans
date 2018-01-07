from back_end.db import DB, STR_LEN


class PlanUser(DB.Model):
    __tablename__ = 'Plan_Users'
    planid = DB.Column(DB.Integer, DB.ForeignKey('Plans.id'), primary_key=True)
    userid = DB.Column(DB.String(STR_LEN), primary_key=True)

    plan = DB.relationship('Plan', backref=DB.backref('users', lazy=True))

    def __init__(self, planid, userid):
        self.planid = planid
        self.userid = userid


def get_plans(userid):
    plans = PlanUser.query.filter_by(userid=userid)
    return [p.plan for p in plans]
