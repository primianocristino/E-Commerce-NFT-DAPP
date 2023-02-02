from flask import render_template, session, request, current_app, redirect, url_for, flash
from werkzeug.utils import secure_filename

from .forms import RegistrationForm, LoginForm, AdminUpdateForm
from .models import User
from src.products.models import AddProduct, Brand, Category
from utils import db, bcrypt, photos

from utils import dex_contract, token_contract

from flask_login import current_user, logout_user

import os
import secrets
import traceback

class AdminManager:
    
    @staticmethod
    def admin():
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
        products = AddProduct.query.all()
        # brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
        # categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
        return render_template(
            'admin/index.html', 
            title='Admin Page', 
            products=products,
            administrator=True if 'email' in session else False,
            contract_info = {
                "abi": dex_contract["abi"],
                "address": dex_contract["address"]
            }
        )

    @staticmethod
    def brands():
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
        brands=  Brand.query.order_by(Brand.id.desc()).all()  
        return render_template('admin/brand.html', title='Brand page', brands=brands, administrator=True if 'email' in session else False)

    @staticmethod
    def categories():
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
        categories=  Category.query.order_by(Category.id.desc()).all()  
        return render_template('admin/brand.html', title='Category page', categories=categories, administrator=True if 'email' in session else False)

    @staticmethod
    def register(): 
        try:
            form=RegistrationForm(request.form)
            if request.method == 'POST' and form.validate():
                hash_password = bcrypt.generate_password_hash(form.password.data)

                image_profile =request.files.get('profile')

                try:
                    if image_profile.filename != "":
                        hash_raw_name = bcrypt.generate_password_hash(image_profile.filename).decode("utf-8")
                        hash_profile_image = secure_filename(hash_raw_name)
                        filename= os.path.join("admin_profile",""+hash_profile_image + '.')
                        image_profile=photos.save(image_profile, name=filename)
                    else:
                        image_profile = None
                except:
                    image_profile = None



                user = User(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password,profile = image_profile)
                db.session.add(user)
                db.session.commit()
                flash(f'Welcome, {form.name.data}. Thanks for registring', 'success')
                return redirect(url_for('login'))
            return render_template('admin/register.html', form=form, title='Registration page', administrator=True if 'email' in session else False)
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash(f'Something went wrong', 'danger')
            return render_template('admin/register.html', form=form, title='Registration page', administrator=True if 'email' in session else False)

    @staticmethod
    def login():
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['email'] = form.email.data 
                flash(f"Welcome, {form.email.data}. You're logged in now", 'success')
                if current_user.is_authenticated:
                    logout_user()
                return redirect(request.args.get('next') or url_for('admin'))
            else:
                flash(f'Wrong password plese try again', 'danger')
        return render_template('admin/login.html', form=form, title='Login Page', administrator=True if 'email' in session else False)

    @staticmethod
    def logout():
        if 'email' not in session:
            flash('An error ocurred.','danger') 
            return redirect(url_for('admin'))
        elif 'email' in session:
                session.pop('email')
                flash('You have been logged out.','success')
                return redirect(url_for('login'))

    @staticmethod
    def profile():
        try:
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            if 'email' in session:
                user_data = User.query.filter_by(email=session["email"]).first()

                return render_template(
                    'admin/profile.html', 
                    title='My Profile', 
                    user_data=user_data, 
                    categories=categories, 
                    brands=brands, 
                    administrator=True if 'email' in session else False,
                    contract_info = {
                        "abi": dex_contract["abi"],
                        "address": dex_contract["address"]
                    },
                    token_info = {
                        "abi": token_contract["abi"],
                        "address": token_contract["address"]
                    })

            else:
                 flash(f'Please login first', 'danger')
                 return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Some thing went wrong.','danger')
            return redirect(url_for('admin'))

    @staticmethod
    def admin_update():
        try:
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            if 'email' in session:
                message_internal = f'Account data have been updated!'
                state_internal = "success"
                
                user_data = User.query.filter_by(email=session["email"]).first()
                form= AdminUpdateForm(user_data, request.form)

                if request.method == "POST" and form.validate():
                    hash_password = None          

                    form_psw = form.password.data
                    form_conf = form.confirm.data
                    
                    # A B     (A and -B) or (-a and B)
                    # F F      F
                    # F T      T
                    # T F      T
                    # T T      F  
                    if (form_psw and not form_conf) or (not form_psw and form_conf):
                        message_internal = "You need to confirm password"
                        state_internal = "danger"
                    
                    elif not form.password.data and not form.confirm.data:
                        hash_password = user_data.password
        
                    else:
                        hash_password= bcrypt.generate_password_hash(form.password.data)

                    if state_internal == "success":
                        image_profile = request.files.get('profile')

                        try:
                            if image_profile != None and image_profile.filename != "":
                                
                                if user_data.profile != None:

                                    old_image_path = os.path.join(
                                        current_app.root_path, 
                                        'static',
                                        'images', 
                                        user_data.profile
                                    )

                                    if os.path.exists(old_image_path):
                                        os.unlink(old_image_path)
                                    
                                hash_raw_name = bcrypt.generate_password_hash(image_profile.filename).decode("utf-8")
                                hash_profile_image = secure_filename(hash_raw_name)
                                filename= os.path.join("admin_profile",""+hash_profile_image + '.')
                                image_profile=photos.save(image_profile, name=filename)
                            else:
                                image_profile = user_data.profile

                        except:
                            image_profile = None
                        
                        old_email = user_data.email
                        user_data.name = form.name.data
                        user_data.username = form.username.data
                        user_data.email= form.email.data
                        user_data.password = hash_password
                        user_data.profile = image_profile
                        
                        db.session.commit()

                        if old_email != form.email.data:
                            logout_user()
                            flash(f'Account updated but login is required!',"success")
                            return redirect(url_for('login'))  
                        else:
                            flash(f'Account updated!',"success")
                            return redirect(url_for('admin_profile'))
                    else:
                        flash(message_internal, state_internal)

                else:
                    user_data = User.query.filter_by(email=session["email"]).first()

                return render_template(
                    'admin/profile_edit.html', 
                    form=form, 
                    user_data=user_data, 
                    categories=categories, 
                    brands=brands, 
                    logged = current_user.is_authenticated, 
                    administrator=True if 'email' in session else False
                    )
            else:
                flash(f'Please login first', 'danger')
                return redirect(url_for('login'))          
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash("Error during profile updating",'danger')
            return render_template(
                'admin/profile.html', 
                title='My Profile', 
                user_data=user_data, 
                categories=categories, 
                brands=brands, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                },
                token_info = {
                    "abi": token_contract["abi"],
                    "address": token_contract["address"]
                })
                