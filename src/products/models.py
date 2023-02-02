from utils import db
from datetime import datetime
from sqlalchemy import DECIMAL
from decimal import Decimal as D


class AddProduct(db.Model):   
    __searchable__= ['name','desc']

    product_id = db.Column(db.String(50), primary_key=True)
    # id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10,8), nullable=False) #0.00000001
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, nullable=False)
    is_nft=db.Column(db.Boolean, nullable=False, default=False)
    nft_hash = db.Column(db.String(200))
     
    desc = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # owner_id = db.Column(db.Integer,db.ForeignKey('register.id'), nullable=False)
    # owner = db.relationship('Register',foreign_keys='AddProduct.owner_id', backref=db.backref('AddProduct_owner_id', lazy=True))

    owner_email = db.Column(db.Integer,db.ForeignKey('register.email'), nullable=False)
    mail = db.relationship('Register',foreign_keys='AddProduct.owner_email', backref=db.backref('AddProduct_owner_email', lazy=True))

    owner_address = db.Column(db.String(50), nullable=False, default=None)

    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    brand = db.relationship('Brand',backref=db.backref('AddProduct_brand', lazy=True))

    category_id= db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('AddProduct_category', lazy=True))

    image_1= db.Column(db.String(150),nullable=False)
    image_2= db.Column(db.String(150),nullable=True, default=None)
    image_3= db.Column(db.String(150),nullable=True, default=None)

    def __repr__(self):
        return '<AddProduct %r>' % self.name

    def as_dict(self):
   
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}   
     
    def as_dict_type(self):
        new_dict = {}
        
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if isinstance(value, D):
                new_dict[c.name] = float(value)
            elif isinstance(value, datetime):
                  new_dict[c.name] = str(value)
            else:
                new_dict[c.name] = value              

        return new_dict

class Brand(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return '<Brand %r>' % self.name

class Category(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(30), nullable=False, unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name