import logging

from flask import Flask, render_template, json, request, redirect, url_for

import back_end as be
import config
from back_end.api import get_userid_from_token
from back_end.exceptions import BaseApiException
from back_end.forms import PlanForm, EventForm, RouteForm

app = Flask(__name__)
app.config.from_object(config)
app.debug = True

be.init(app)

from back_end import db
from back_end.db import plans, events, routes


# DEV reset
@app.route('/reset', methods=['GET'])
def reset():
    if not app.debug:
        # TODO throw error
        return 'Nope :)'
    be.db.reset()
    return 'Reset!'


# [homepage]
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# [plan view]
@app.route('/<planid>', methods=['GET'])
def disp_plan(planid):
    token = request.headers.get('vp-token')
    if token is None:
        # TODO change this to template with script to redo request with header
        return redirect(url_for('index'))
    try:
        userid = get_userid_from_token(token)
        plan = be.db.plans.get_from_id(planid, userid)
        plan_json = json.dumps(plan.serialise)
        events_json = json.dumps([i.serialise for i in plan.events])
        routes_json = json.dumps([i.serialise for i in plan.routes])
    except BaseApiException:
        return redirect(url_for('index'))
    return render_template('plan.html',
                           plan=plan,
                           planJsonStr=plan_json,
                           eventJsonStr=events_json,
                           routeJsonStr=routes_json)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace
    logging.exception('An error occurred during a request.\n{}'.format(e))
    return 'An internal error occurred.', 500


# TODO remove functions below

# [homepage]
@app.route('/loginT', methods=['GET'])
def login():
    return render_template('loginT.html')


# [homepage]
@app.route('/logoutT', methods=['GET'])
def logout():
    return render_template('logoutT.html')


# [new plan]
@app.route('/plan/new', methods=['POST', 'GET'])
def new_plan():
    if (request.method == "GET"):
        form = PlanForm()
        return render_template('new_plan.html', form=form)
    elif (request.method == 'POST'):
        # create new plan in db
        newPlan = be.db.plans.create(request.form['name'])
        return redirect(url_for('disp_plan', planid=newPlan.id))


# [new event]
@app.route('/plan/<planid>/event/new', methods=['POST', 'GET'])
def new_event(planid):
    if (request.method == "GET"):
        form = EventForm()
        plan = be.db.plans.get_from_id(planid)
        return render_template('new_event.html', form=form, plan=plan)

    elif (request.method == 'POST'):
        e = be.db.events.create(planid, request.form['name'], request.form['location'])
        return redirect(url_for('disp_plan', planid=e.plan.id))


# [new route]
@app.route('/plan/<planid>/route/new', methods=['POST', 'GET'])
def new_route(planid):
    if (request.method == "GET"):
        form = RouteForm()
        plan = be.db.plans.get_from_id(planid)
        return render_template('new_route.html', form=form, plan=plan)
    elif (request.method == 'POST'):
        r = be.db.routes.create(planid, request.form['name'], list(map(int, (request.form['eventids']).split(','))))
        return redirect(url_for('disp_plan', planid=r.plan.id))


# [count votes]
@app.route('/plan/<planid>/countvotes', methods=['POST'])
def countvotes(planid):
    plan = be.db.plans.countvotes(planid)
    return redirect(url_for('disp_plan', planid=plan.id))


# [vote]
@app.route('/event/<eventid>/upvote', methods=['POST'])
def upvote_event(eventid):
    e = be.db.events.upvote(eventid)
    return redirect(url_for('disp_plan', planid=e.planid))


@app.route('/event/<eventid>/downvote', methods=['POST'])
def downvote_event(eventid):
    e = be.db.events.downvote(eventid)
    return redirect(url_for('disp_plan', planid=e.planid))


@app.route('/route/<routeid>/upvote', methods=['POST'])
def upvote_route(routeid):
    r = be.db.routes.upvote(routeid)
    return redirect(url_for('disp_plan', planid=r.planid))


@app.route('/route/<routeid>/downvote', methods=['POST'])
def downvote_route(routeid):
    r = be.db.routes.downvote(routeid)
    return redirect(url_for('disp_plan', planid=r.planid))
