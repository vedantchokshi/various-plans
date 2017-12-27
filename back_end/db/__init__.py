from flask_sqlalchemy import SQLAlchemy

# MUST reset the db, using reset() after changing default_str_len
default_str_len = 100

def init(app):
    global db
    db = SQLAlchemy(app)
    import plans, events, routes, route_events
    db.create_all()

def reset():
    db.drop_all()