from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField


class PlanForm(FlaskForm):
    # TODO TextField is deprecated
    name = TextField("Name Of Plan")
    submit = SubmitField("Create!")
