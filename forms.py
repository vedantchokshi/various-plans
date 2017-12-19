from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField

class PlanForm(FlaskForm):
   name = TextField("Name Of Plan")
   submit = SubmitField("Create!")
