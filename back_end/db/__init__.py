"""
Initialise database
"""
from flask_sqlalchemy import SQLAlchemy

STR_LEN = 50

# db variable should exist from the start
# has helped debug in the past
DB = SQLAlchemy()


def init(app):
    """
    Initialise database variable with Flask app
    """
    # pylint: disable-msg=global-statement
    # Database variable needs to be accessible by all files in this module
    global DB
    DB = SQLAlchemy(app)
    import_all()


def reset():
    """
    Reset database, drop all tables and create again from model definitions in this module
    """
    DB.drop_all()
    import_all()
    DB.create_all()


def import_all():
    """
    Imports for all models defined in this module
    """
    # pylint: disable-msg=cyclic-import
    # Imports are safe as they are called inside init and reset functions
    # pylint: disable-msg=unused-variable
    # Imports are used by database
    import back_end.db.plans
    import back_end.db.events
    import back_end.db.routes
    import back_end.db.route_events
    import back_end.db.votes
    import back_end.db.plan_users
