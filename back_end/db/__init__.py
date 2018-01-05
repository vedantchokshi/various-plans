from flask_sqlalchemy import SQLAlchemy

default_str_len = 100

# db variable should exist from the start
# has helped debug in the past
db = SQLAlchemy()


def init(app):
    global db
    db = SQLAlchemy(app)
    import_all()


def reset():
    db.drop_all()
    import_all()
    db.create_all()


def import_all():
    import plans, events, routes, route_events, votes, plan_users
