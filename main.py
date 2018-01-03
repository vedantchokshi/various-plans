import logging

from flask import Flask, render_template, json, request, redirect, url_for

import back_end as be
import config
from back_end.api import get_userid_from_token
from back_end.exceptions import BaseApiException

app = Flask(__name__)
app.config.from_object(config)
# TODO change when final release
app.debug = True

be.init(app)

from back_end import db
from back_end.db import plans, routes

if app.debug:
    # DEV reset
    @app.route('/reset', methods=['GET'])
    def reset():
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
