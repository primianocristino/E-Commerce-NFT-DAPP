from wtforms import Form, StringField, PasswordField, SubmitField, validators,ValidationError
from flask_wtf.file import FileAllowed, FileField, FileRequired
from utils import bcrypt
from .models import User

import re

class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25),validators.DataRequired()])
    username = StringField('Username', [validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField('Email Address', [validators.DataRequired(),validators.Email()])
    password = PasswordField('New Password', [
        validators.Length(min=8, max=25),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    profile= FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'],'Image only, PLEASE!')])
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('This username is already in use!')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already in use!')    

class AdminUpdateForm(Form):
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

    profile= FileField('Profile', validators=[FileAllowed(['jpg','png','jpeg','gif'],'Image only, PLEASE!')])

    def __init__(self, profile_data, request_form):
        # if request_form == None:
        super().__init__(request_form)
        # else:
        #     FlaskForm.__init__(self, request_form)
            
        self.old_profile_data = profile_data

    def validate_username(self, username):
        if username.data != "" and username.data != self.old_profile_data.username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError('This username is already in use!')

    def validate_email(self, email):
        if email.data != "" and email.data != self.old_profile_data.email:
            at_index = email.data.find("@")
            email_points = [m.start() for m in re.finditer('.', email.data)]

            if at_index < 0 or  at_index > email_points[-1]:
                raise ValidationError("Invalid email address")

            if User.query.filter_by(email=email.data).first():
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



class LoginForm(Form):
    email = StringField('Email Address:', [validators.DataRequired(),validators.Email()])
    password = PasswordField('Password:', [validators.DataRequired()])
    