from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import IntegerField, StringField, BooleanField, TextAreaField, Form, validators, DecimalField
class Addproducts(Form):
    name= StringField('Name',[validators.DataRequired()])
    price= DecimalField('Price',[validators.DataRequired(), validators.NumberRange(min=0)],places=8)
    discount= IntegerField('Discount', default=0, validators =[validators.NumberRange(min=0)])
    stock= DecimalField('Stock', [validators.DataRequired(),validators.NumberRange(min=0)],places=0)
    description= TextAreaField('Description', [validators.DataRequired()])


    image_1= FileField('Image 1', validators=[FileAllowed(['jpg','png','gif','jpeg'])])
    image_2= FileField('Image 2', validators=[FileAllowed(['jpg','png','gif','jpeg'])])
    image_3= FileField('Image 3', validators=[FileAllowed(['jpg','png','gif','jpeg'])])