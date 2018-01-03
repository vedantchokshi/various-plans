from flask_sqlalchemy import SQLAlchemy

default_str_len = 100

db = SQLAlchemy()


def init(app):
    global db
    db = SQLAlchemy(app)
    import plans
    import events
    import routes
    import route_events


def reset():
    global db
    db.drop_all()
    import plans
    import events
    import routes
    import route_events
    db.create_all()
