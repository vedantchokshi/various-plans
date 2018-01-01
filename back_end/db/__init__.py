from flask_sqlalchemy import SQLAlchemy

# MUST reset the db, using reset() after changing default_str_len
default_str_len = 100

db = SQLAlchemy()


def init(app):
    global db
    db = SQLAlchemy(app)
    import plans, events, routes, route_events


def reset():
    global db
    db.drop_all()
    import plans, events, routes, route_events
    db.create_all()


def authenticate_user_plan(planid, userid):
    # AUTHTODO check that in the userplan table there is a record with userplan.userid=userid and userplan.planid=planid
    # May have to return all records where the userplan.userid=userid and then check one has a planid of planid. (cos objects)
    # return true or false depending on result
    return True