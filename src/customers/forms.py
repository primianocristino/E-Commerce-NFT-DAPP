from wtforms import StringField, PasswordField, SubmitField, SelectField, HiddenField, BooleanField
from wtforms import Form, widgets, validators, ValidationError

from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm
from utils import bcrypt
from .models import Register


import re

class MultiCheckboxField(SelectField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CustomerRegisterForm(FlaskForm):
    name= StringField('Name:',[validators.DataRequired()])
    username= StringField('Username:',[validators.Length(min=4, max=25),validators.DataRequired()])
    email= StringField('Email:', [
        validators.Email(), 
        validators.DataRequired()
        ])
    password= PasswordField('Password:', [
        validators.Length(min=8, max=25), 
        validators.DataRequired(), 
        validators.EqualTo('confirm', message='Both password must match.')
        ])
    confirm= PasswordField('Repeat Password:', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Both password must match.')
        ])
    country= StringField('Country:', [validators.DataRequired()])
    city= StringField('City:', [validators.DataRequired()])
    contact= StringField('Contact:', [validators.DataRequired()])
    address= StringField('Address:', [validators.DataRequired()])
    zipcode= StringField('Zipcode:', [validators.DataRequired()])

    profile= FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'],'Image only, PLEASE!')])

    conditionTerms = MultiCheckboxField('ConditionTerms', coerce=bool,choices=[(True,"Agree")])
    registerAccount = HiddenField("")
    submit= SubmitField('Register')

    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already in use!')

    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already in use!')        
# =========================================================
class CustomerUpdateForm(FlaskForm):
    name= StringField('Name:',[])
    username= StringField('Username:',[validators.Length(min=4, max=25)])
    email= StringField('Email:', [
        validators.Email(), 
        ])
    currentpassword = PasswordField('Current password', [])
    password= PasswordField('Password:', [ 
        validators.EqualTo('confirm', message='Both password must match.')
        ])
    confirm= PasswordField('Repeat Password:', [
        validators.EqualTo('password', message='Both password must match.')
    ])
    country= StringField('Country:', [])
    city= StringField('City:', [])
    contact= StringField('Contact:', [])
    address= StringField('Address:', [])
    zipcode= StringField('Zipcode:', [])

    profile= FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'],'Image only, PLEASE!')])
    conditionTerms = BooleanField('ConditionTerms')
    submit= SubmitField('Update')

    def __init__(self, profile_data):
        # if request_form == None:
        FlaskForm.__init__(self)
        # else:
        #     FlaskForm.__init__(self, request_form)
            
        self.old_profile_data = profile_data

    def validate_username(self, username):
        if username.data != "" and username.data != self.old_profile_data.username:
            if Register.query.filter_by(username=username.data).first():
                raise ValidationError('This username is already in use!')

    def validate_email(self, email):
        if email.data != "" and email.data != self.old_profile_data.email:
            at_index = email.data.find("@")
            email_points = [m.start() for m in re.finditer('.', email.data)]

            if at_index < 0 or  at_index > email_points[-1]:
                raise ValidationError("Invalid email address")

            if Register.query.filter_by(email=email.data).first():
                raise ValidationError('This email is already in use!')     

    def validate_currentpassword(self, currentpassword):

        if currentpassword.data != "" and not bcrypt.check_password_hash(self.old_profile_data.password, currentpassword.data):
            raise ValidationError("Invalid password")

        if currentpassword.data == "" and self.password.data != "":
            raise ValidationError("Current password is needed")

        if currentpassword.data != "" and self.password.data == "":
            raise ValidationError("Do you want to change the password?")
             
    def validate_password(self, password):
        
        if password.data != "" and not bcrypt.check_password_hash(self.old_profile_data.password, password.data):
            if len(password.data) < 8 or len(password.data) > 25:
                raise ValidationError('Invalid password')
class CustomerLoginForm(FlaskForm):
    email= StringField('Email:', [validators.Email(), validators.DataRequired()])
    password= PasswordField('Password:', [validators.DataRequired()])
    submit= SubmitField('Login')
