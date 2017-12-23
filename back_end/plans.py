from datetime import datetime
from . import db

class Plan(db.Model):
    __tablename__ = 'Plans'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phase = db.Column(db.Integer, nullable=False)
    startDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    endDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, name, startDate=datetime.utcnow, endDate = datetime.utcnow):
        self.name = name
        self.phase = 1

def get_from_id(planid):
    try:
        return Plan.query.get(int(planid))
    except ValueError:
        return None

def create(name):
    newPlan = Plan(name)
    db.session.add(newPlan)
    db.session.commit()
    return newPlan

def countvotes(planid):
    plan = get_from_id(planid)
    plan.phase = plan.phase + 1
    db.session.commit()
    return plan
