from flask_sqlalchemy import SQLAlchemy

# MUST reset the db, using reset() after changing default_str_len
default_str_len = 100

db = SQLAlchemy()


def init(app):
    global db
    db = SQLAlchemy(app)
    import plans, events, routes, route_events


def reset(app):
    db.drop_all()
    import plans, events, routes, route_events
    db.create_all()
