from flask_sqlalchemy import SQLAlchemy

default_str_len = 100

db = SQLAlchemy()


def init(app):
    global db
    db = SQLAlchemy(app)
    import_all()


def reset():
    global db
    db.drop_all()
    import_all()
    db.create_all()


def import_all():
    import plans
    import events
    import routes
    import route_events
    import votes
    import plan_users