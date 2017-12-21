from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField

# TODO VERIFY ALL FIELDS ARE CORRECT TYPES AND ADD VALIDATION

class PlanForm(FlaskForm):
    # TODO TextField is deprecated
    name = TextField("Name Of Plan")
    submit = SubmitField("Create!")

class EventForm(FlaskForm):
    # TODO TextField is deprecated
    name = TextField("Name Of Event")
    location = TextField("Location Of Event")
    submit = SubmitField("Create!")

class RouteForm(FlaskForm):
    # TODO TextField is deprecated
    name = TextField("Name Of Route")
    eventids = TextField("Comma separated event nos.")
    submit = SubmitField("Create!")
