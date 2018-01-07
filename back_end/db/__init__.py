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
    # pylint: disable-msg=cyclic-import
    # Imports are safe as they are called inside init and reset functions
    # pylint: disable-msg=unused-variable
    # Imports are used by database
    import plans
    import events
    import routes
    import route_events
    import votes
    import plan_users
