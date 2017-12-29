import logging

from flask import Flask, render_template

import back_end as be
import config

app = Flask(__name__)
app.config.from_object(config)
app.debug = True

be.init(app)

from back_end import db
from back_end.db import plans


# TDEV reset
@app.route('/reset', methods=['GET'])
def reset():
    if not app.debug:
        # TODO throw error
        return 'Nope :)'
    be.db.reset()
    return 'Reset!'


# [homepage]
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


# [plan view]
@app.route('/#/<planid>', methods=['GET'])
def disp_plan(planid):
    plan = be.db.plans.get_from_id(planid)
    return render_template('plan.html', plan=plan)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
