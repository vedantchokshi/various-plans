# [START imports]
import logging
from flask import Flask, render_template, request, redirect, url_for
from forms import PlanForm, EventForm, RouteForm
import back_end as be
import config

app = Flask(__name__)
app.config.from_object(config)
app.debug = True

be.init(app)


# DEV
@app.route('/reset', methods=['GET'])
def reset():
    be.reset()
    return 'Reset!'

# [homepage]
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


# [plan view]
@app.route('/plan/<planid>', methods=['GET'])
def disp_plan(planid):
    plan = be.plans.get_from_id(planid)
    return render_template('plan.html', plan=plan)


# [new plan]
@app.route('/plan/new', methods=['POST', 'GET'])
def new_plan():
    if (request.method == "GET"):
        form = PlanForm()
        return render_template('new_plan.html', form=form)
    elif (request.method == 'POST'):
        # create new plan in db
        newPlan = be.plans.create(request.form['name'])
        return redirect(url_for('disp_plan', planid=newPlan.id))


# [new event]
@app.route('/plan/<planid>/event/new', methods=['POST', 'GET'])
def new_event(planid):
    if (request.method == "GET"):
        form = EventForm()
        plan = be.plans.get_from_id(planid)
        return render_template('new_event.html', form=form, plan=plan)

    elif (request.method == 'POST'):
        e = be.events.create(planid, request.form['name'], request.form['location'])
        return redirect(url_for('disp_plan', planid=e.plan.id))


# [new route]
@app.route('/plan/<planid>/route/new', methods=['POST', 'GET'])
def new_route(planid):
    if (request.method == "GET"):
        form = RouteForm()
        plan = be.plans.get_from_id(planid)
        return render_template('new_route.html', form=form, plan=plan)
    elif (request.method == 'POST'):
        r = be.routes.create(planid,request.form['name'],list(map(int, (request.form['eventids']).split(','))))
        return redirect(url_for('disp_plan', planid=r.plan.id))


# [count votes]
@app.route('/plan/<planid>/countvotes', methods=['POST'])
def countvotes(planid):
    plan = be.plans.countvotes(planid)
    return redirect(url_for('disp_plan', planid=plan.id))


# [vote]
@app.route('/event/<eventid>/upvote', methods=['POST'])
def upvote_event(eventid):
    e = be.events.upvote(eventid)
    return redirect(url_for('disp_plan', planid=e.planid))


@app.route('/event/<eventid>/downvote', methods=['POST'])
def downvote_event(eventid):
    e = be.events.downvote(eventid)
    return redirect(url_for('disp_plan', planid=e.planid))


@app.route('/route/<routeid>/upvote', methods=['POST'])
def upvote_route(routeid):
    r = be.routes.upvote(routeid)
    return redirect(url_for('disp_plan', planid=r.planid))


@app.route('/route/<routeid>/downvote', methods=['POST'])
def downvote_route(routeid):
    r = be.routes.downvote(routeid)
    return redirect(url_for('disp_plan', planid=r.planid))


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
