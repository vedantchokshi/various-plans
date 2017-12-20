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
from forms import PlanForm
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

    def vote(self, vote):
        self.votes = self.votes + vote


class Route(db.Model):
    __tablename__ = 'Routes'
    id = db.Column('id',db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    planid = db.Column(db.Integer, db.ForeignKey('Plans.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)


    plan = db.relationship('Plan', backref=db.backref('routes', lazy=True))

    def __init__(self, name):
       self.name = name

db.create_all()

# [homepage]
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


# [plan view]
@app.route('/plan/<planid>', methods=['GET'])
def disp_plan(planid):
    # get plan form db or smth
    plan = Plan.query.get(planid)
    return render_template('plan.html', plan=plan)


# [newplan]
@app.route('/plan/new', methods=['POST', 'GET'])
def new_plan():
    if (request.method == "GET"):
        form = PlanForm()
        return render_template('new_plan.html', form=form)
    elif (request.method == 'POST'):
        # create new plan in db
        newPlan = Plan(request.form['name'],1)

        e1 = Event('Booze up','Stags')
        e2 = Event('Phil\'s sexy dnace moves','Sobar')
        newPlan.events.append(e1)
        newPlan.events.append(e2)

        newPlan.routes.append(Route('Route 1'))

        db.session.add(newPlan)
        db.session.commit()

        return disp_plan(newPlan.id)

# [vote]
@app.route('/event/<eventid>/upvote', methods=['POST','GET'])
def upvote_event(eventid):
    return vote_event(eventid,1)

@app.route('/plan/<planid>/event/<eventid>/downvote', methods=['POST'])
def dwonvote_event(eventid):
    return vote_event(eventid,-1)


def vote_event(eventid,vote):
    event = Event.query.get(eventid)
    event.vote(vote)
    db.session.commit()
    return str(event.votes)

@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


if __name__ == '__main__':
    app.run(debug=True)
