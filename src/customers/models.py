from utils import db, login_manager
from datetime import datetime
from flask_login import UserMixin
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.dialects.postgresql import JSON

import json


@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)

class Register(db.Model, UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(50), unique=False)
    username= db.Column(db.String(50), unique=True)
    email= db.Column(db.String(50), unique=True)
    password= db.Column(db.String(150), unique=False)
    country= db.Column(db.String(50), unique=False)
    city= db.Column(db.String(50), unique=False)
    contact= db.Column(db.String(50), unique=False)
    address= db.Column(db.String(50), unique=False)
    zipcode= db.Column(db.String(50), unique=False)
    profile= db.Column(db.String(200), unique=False, default='profile.jpg')
    date_created= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Register %r>' % self.name


class JsonEcodeDict(db.TypeDecorator):
    impl= db.Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value) 

    def process_result_value(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.loads(value) 


class CustomerOrder(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    invoice= db.Column(db.String(50), unique=True, nullable=False)
    # status= db.Column(db.String(20), nullable=False, default='Pending')
    customer_id= db.Column(db.Integer, nullable=False, unique=False)
    date_created= db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    orders= db.Column(JsonEcodeDict)
    # orders= db.Column(db.Array(db.Integer))

    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice

'''
class ProductOrder(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    product_id= db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, default=0)
    image= db.Column(db.String(150),nullable=False, default='image.jpg')
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<ProductOrder %r>' % self.name
'''