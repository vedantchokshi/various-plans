# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

# [START imports]
from flask import Flask, render_template, request
from forms import PlanForm, EventForm, RouteForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'development key lol'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vplans_db:COMP3207Plans@tuddenham.no-ip.org:3306/variousplans'
 # 'mysql+mysqldb://root@/<dbname>?unix_socket=/cloudsql/<projectid>:<instancename>'

db = SQLAlchemy(app)

class Plan(db.Model):
   __tablename__ = 'Plans'
   id = db.Column('id',db.Integer, primary_key = True)
   name = db.Column(db.String(100), nullable=False)
   phase = db.Column(db.Integer, nullable =False)
   startDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   endDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

   def __init__(self, name, phase):
       self.name = name
       self.phase = phase

class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column('id',db.Integer, primary_key = True)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location  = db.Column(db.String(100))
    votes = db.Column(db.Integer, nullable=False, default=0)

    plan = db.relationship('Plan', backref=db.backref('events', lazy=True))

    def __init__(self, name, location):
       self.name = name
       self.location = location
       self.votes = 0

    def vote(self, vote):
        self.votes = self.votes + vote


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id',db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)


    plan = db.relationship('Plan', backref=db.backref('routes', lazy=True))
    events = db.relationship("Event",  secondary='route_event')

    def __init__(self, name):
        self.name = name
        self.votes = 0

    def vote(self, vote):
        self.votes = self.votes + vote

    def assignEvents(self, eventids):
        for i,eventid in enumerate(eventids):
           db.session.add(RouteEvent(self.id, eventid, i))

class RouteEvent(db.Model):
    __tablename__ = 'route_event'
    routeid = db.Column(db.Integer, db.ForeignKey('Routes.id'), primary_key=True)
    eventid = db.Column(db.Integer, db.ForeignKey('Events.id'), primary_key=True)
    index = db.Column(db.Integer,  primary_key=True, nullable = False)

    # events = db.relationship('Event', backref=db.backref('event', lazy=True))
    def __init__(self, routeid, eventid, index):
        self.routeid = routeid
        self.eventid = eventid
        self.index = index

db.create_all()

# [homepage]
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


# [plan view]
@app.route('/plan/<planid>', methods=['GET'])
def disp_plan(planid):
    # cant we redirect as well, to allow refreshes
    plan = Plan.query.get(planid)
    return render_template('plan.html', plan=plan)


# [new plan]
@app.route('/plan/new', methods=['POST', 'GET'])
def new_plan():
    if (request.method == "GET"):
        form = PlanForm()
        return render_template('new_plan.html', form=form)
    elif (request.method == 'POST'):
        # create new plan in db
        newPlan = Plan(request.form['name'],1)

        db.session.add(newPlan)
        db.session.commit()
        return disp_plan(newPlan.id)

# [new event]
@app.route('/event/new', methods=['POST', 'GET'])
def new_event():
    if (request.method == "GET"):
        form = EventForm()
        return render_template('new_event.html', form=form)
    elif (request.method == 'POST'):

        e = Event(request.form['name'],request.form['location'])
        plan = Plan.query.get(int(request.form['planid']))
        plan.events.append(e)
        db.session.commit()
        return disp_plan(plan.id)

# [new route]
@app.route('/route/new', methods=['POST', 'GET'])
def new_route():
    if (request.method == "GET"):
        form = RouteForm()
        return render_template('new_route.html', form=form)
    elif (request.method == 'POST'):

        plan = Plan.query.get(int(request.form['planid']))
        # TODO check the phase!!

        r = Route(request.form['name'])
        plan.routes.append(r)
        db.session.commit()

        # TODO check events are in the plan!!
        r.assignEvents(list(map(int,request.form['eventids'].split(','))))
        db.session.commit()

        return disp_plan(plan.id)

# [count votes]
@app.route('/plan/<planid>/countvotes', methods=['POST'])
def countvotes(planid):
    plan = Plan.query.get(planid)
    plan.phase = plan.phase + 1

# [vote]
@app.route('/event/<eventid>/upvote', methods=['POST'])
def upvote_event(eventid):
    return vote_event(eventid,1)

@app.route('/event/<eventid>/downvote', methods=['POST'])
def downvote_event(eventid):
    return vote_event(eventid,-1)


def vote_event(eventid,vote):
    # TODO check plan is in phase 1
    event = Event.query.get(eventid)
    event.vote(vote)
    db.session.commit()
    return str(event.votes)

@app.route('/route/<routeid>/upvote', methods=['POST'])
def upvote_route(routeid):
    return vote_route(routeid,1)

@app.route('/route/<routeid>/downvote', methods=['POST'])
def downvote_route(routeid):
    return vote_route(routeid,-1)


def vote_route(eventid,vote):
    # todo check plan is in phase 2
    route = Route.query.get(routeid)
    route.vote(vote)
    db.session.commit()
    return str(route.votes)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run(debug=True)
