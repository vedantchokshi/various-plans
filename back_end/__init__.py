from flask_sqlalchemy import SQLAlchemy

def init(app):
    global db
    db = SQLAlchemy(app)
    import plans, events, routes, route_events
    db.create_all()

def reset():
    db.drop_all()
