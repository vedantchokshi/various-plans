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

# Imports must be done after back_end.init(app)
from back_end import db
from back_end.db import plans


# reset
@app.route('/reset', methods=['GET'])
def reset():
    admins = [
        111355985876555375664,
        110280863980572958575
    ]
    try:
        token = request.cookies.get('vp-token')
        if token is None:
            raise ValueError
        userid = get_userid_from_token(token)
        if userid in admins:
            be.db.reset()
            return 'Reset!'
        else:
            return 'You are not an admin...'
    except Exception:
        pass
    finally:
        return redirect(url_for('index'))


# [homepage]
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# [helppage]
@app.route('/help', methods=['GET'])
def disp_help():
    return render_template('help.html')


# [plan view]
@app.route('/<planid>', methods=['GET'])
def disp_plan(planid):
    token = request.cookies.get('vp-token')
    if token is None:
        return redirect(url_for('index'))
    try:
        userid = get_userid_from_token(token)
        plan = be.db.plans.get_from_id(planid, userid)
    except BaseApiException:
        return redirect(url_for('index'))
    return render_template('main.html', plan=plan)


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace
    logging.exception('An error occurred during a request.\n{}'.format(e))
    return 'An internal error occurred.', 500
