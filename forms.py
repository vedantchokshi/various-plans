from flask_wtf import Form
from wtforms import TextField, SubmitField

class PlanForm(Form):
   name = TextField("Name Of Plan")
   submit = SubmitField("Create!")
