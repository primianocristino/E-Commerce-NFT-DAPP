from flask import redirect, render_template, url_for, flash, request, session

from flask_login import current_user, logout_user, login_user
from werkzeug.utils import secure_filename
from sqlalchemy.orm.attributes import flag_modified

from .forms import CustomerRegisterForm, CustomerLoginForm, CustomerUpdateForm
from .models import Register, CustomerOrder
from src.products.models import AddProduct
from src.products.routes import *
from utils import db, bcrypt, photos

from utils import dex_instance, dex_contract, token_contract, token_nft_contract

import os
import secrets
import traceback



class CustomerManager: 
    @staticmethod
    def MergeDicts(dict1, dict2):
        if isinstance(dict1, list) and isinstance(dict2, list):
            return dict1 + dict2
        elif isinstance(dict1, dict) and isinstance(dict2, dict):
            return dict(list(dict1.items()) + list(dict2.items()))
        return False

    @staticmethod
    def customer():
        if not current_user.is_authenticated:
            flash(f'Please login first', 'danger')
            return redirect(url_for('customer_login'))

        # email = current_user.email
        # owner_id = Register.query.filter_by(email=email).first()
        products = AddProduct.query.filter_by(owner_email=current_user.email).all()

        product_owner_addresses = []

        for product in products:
            hidden_address = product.owner_address[0:5] +"..."+product.owner_address[-4:]
            product_owner_addresses.append(hidden_address)
            # product.owner_address=hidden_address

        brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
        categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
        return render_template(
            'customer/index.html', 
            title='Customer Page', 
            products=products,
            hidden_addresses = product_owner_addresses,
            categories=categories, 
            brands=brands, 
            logged = current_user.is_authenticated, 
            administrator=True if 'email' in session else False,
            contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                }
        )

    @staticmethod
    def customer_register():
        catch_error_message = f'Something went wrong'
        try:
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            form= CustomerRegisterForm()
            if form.validate_on_submit():

                # accountAddress = request.form.get('registerAccount')

                # accountAddress = form.registerAccount.data
                # accountAddress = dex_instance["value"].Web3.toChecksumAddress(accountAddress)

                # approved = dex_instance["value"].token_nft.isApprovedForAll(accountAddress, dex_contract["address"])

                # if not approved:
                #     catch_error_message = f"ConditionTerms are not approved"
                #     raise Exception("ConditionTerms are not approved")
                # if True: # else:
                # print()
                # print("COSA HA SCELTO??")
                # print(form.conditionTerms.data)
                # print()
                # return redirect(url_for('customer_login'))
                hash_password= bcrypt.generate_password_hash(form.password.data)
                image_profile = form.profile.data
                try:
                    if image_profile.filename != "":
                        hash_raw_name = bcrypt.generate_password_hash(image_profile.filename).decode("utf-8")
                        hash_profile_image = secure_filename(hash_raw_name)
                        filename= os.path.join("customer_profile",""+hash_profile_image + '.')
                        image_profile=photos.save(image_profile, name=filename)
                    else:
                        image_profile = None
                except:
                    image_profile = None
                
                register= Register(
                    name=form.name.data, 
                    username=form.username.data,
                    email=form.email.data, 
                    password=hash_password, 
                    country=form.country.data,
                    city=form.city.data, 
                    address=form.address.data, 
                    contact=form.contact.data,
                    zipcode=form.zipcode.data, 
                    profile = image_profile
                )
                db.session.add(register)
                flash(f'Welcome {form.name.data}. Thank you for registering!','success')
                db.session.commit()
                return redirect(url_for('customer_login'))

            return render_template(
                'customer/register.html', 
                form=form, 
                categories=categories, 
                brands=brands, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                },
                token_nft_info = {
                    "abi": token_nft_contract["abi"],
                    "address": token_nft_contract["address"]
                })
                
        
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash(catch_error_message, 'danger')          
            return render_template(
                'customer/register.html', 
                form=form, 
                categories=categories, 
                brands=brands, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False
            )

    @staticmethod
    def customer_login():
        form= CustomerLoginForm()
        if form.validate_on_submit():
            user= Register.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                next= request.args.get('next')
                if 'email' in session:
                    session.pop('email')
                return redirect(next or url_for('home'))
            else:    
                flash('Incorrect email and password. Try again','danger')  
                return redirect(url_for('customer_login'))  
        brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
        categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
        return render_template(
            'customer/login.html', 
            form=form, 
            categories=categories, 
            brands=brands, 
            logged = current_user.is_authenticated, 
            administrator=True if 'email' in session else False
            )

    @staticmethod
    def customer_logout():
        logout_user()
        flash('You have been logged out.','success')
        return redirect(url_for('home'))

    @staticmethod
    def customer_update():
        try:
            message_internal = f'Account data have been updated!'
            state_internal = "success"
            
            customer_id= current_user.id
            user_data= Register.query.filter_by(id=customer_id).first()

            form= CustomerUpdateForm(user_data)

            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()

            validate = form.validate_on_submit()
            if validate:
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
                    image_profile = form.profile.data
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
                            filename= os.path.join("customer_profile",""+hash_profile_image + '.')
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
                    user_data.country = form.country.data
                    user_data.city = form.city.data
                    user_data.address = form.address.data
                    user_data.contact = form.contact.data
                    user_data.zipcode = form.zipcode.data
                    user_data.profile = image_profile

                    products = AddProduct.query.filter_by(owner_email=old_email).all()

                    for product in products:
                        product.owner_email = user_data.email
                    
                    db.session.commit()

                    if old_email != form.email.data:
                        logout_user()
                        flash(f'Account updated but login is required!',"success")
                        return redirect(url_for('customer_login'))  
                    else:
                        flash(f'Account updated!',"success")
                        return redirect(url_for('profile'))
                else:
                    flash(message_internal, state_internal)

            else:
                user_data= Register.query.filter_by(id=customer_id).first()

            return render_template(
                'customer/profile_edit.html', 
                form=form, 
                user_data=user_data, 
                categories=categories, 
                brands=brands, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                },
                token_nft_info = {
                    "abi": token_nft_contract["abi"],
                    "address": token_nft_contract["address"]
                }
                )
        
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash("Error during profile updating",'danger')
            return render_template(
                'customer/profile.html', 
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

    @staticmethod
    def customer_delete():
        try:
            user_id = current_user.id
            if current_user.is_authenticated:    
                logout_user()
                user = Register.query.filter_by(id=user_id).first()
                db.session.delete(user)
                db.session.commit()
                flash('Account has been removed successfully.','success')
            else:
                flash('No account is logged.','danger')
            return redirect(url_for('customer_login'))
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash('Some thing went wrong durring account removing.','danger')
            return redirect(url_for('home'))
        
    @staticmethod
    def getorder():
        try:
            if current_user.is_authenticated:
                customer_id= current_user.id
                invoice= secrets.token_hex(16)
                DictItems ={}
                products = []

                if 'Shoppingcart' not in session:
                    return redirect(url_for('getcart'))

                for key in session['Shoppingcart'].keys():
                    product = AddProduct.query.filter_by(product_id=key).first()
        
                    item = {str(key): {
                    'discount': product.discount, 'image_1': product.image_1, 'name': product.name, 'price':float(product.price), 
                    'quantity':session['Shoppingcart'][str(key)]['quantity'], 'stock':product.stock,'product_id':product.product_id, 'status': 'Pending', "is_nft":product.is_nft}}   
                    
                    item1 = {str(key):{**product.as_dict_type(), **{'status': 'Pending', 'quantity':session['Shoppingcart'][str(key)]['quantity']}}}

                    DictItems = CustomerManager.MergeDicts(DictItems,item1)

                    if int(session['Shoppingcart'][str(key)]['quantity']) > int(product.stock):
                        message = "Product " + str(product.name) + " is out of order"
                        flash(message,'danger')
                        return redirect(url_for('getcart'))
        
                    product.stock -= int(session['Shoppingcart'][str(key)]['quantity'])
                    #TODO
                    #change owner in database if nft
                    if product.is_nft: 
                        _,_,_,_,remoteAddress,_ = dex_instance["value"].getProduct(product.product_id)
                        remoteAddress = dex_instance["value"].Web3.toChecksumAddress(remoteAddress) 
                        product.owner_address=remoteAddress       
                        product.owner_email=current_user.email
     

                order= CustomerOrder(invoice=invoice, customer_id=customer_id, orders=DictItems)
                
                db.session.add(order)
                db.session.commit()
                session.pop('Shoppingcart')
                session.modified=True
                flash('Your order has been sent success.','success')
                return redirect(url_for('orders', invoice=invoice))

        except Exception as e:
            print(e)
            traceback.print_exc()
            flash('Some thing went wrong while get order.','danger')
            return redirect(url_for('getcart'))

    @staticmethod
    def orders(invoice):
        try: 
            if current_user.is_authenticated:
                grandTotal= 0
                subTotal=0
                customer_id= current_user.id
                customer= Register.query.filter_by(id=customer_id).first()
                orders= CustomerOrder.query.filter_by(invoice=invoice).first()

                if (orders is None):
                    flash('Some thing went wrong while getting the order.','danger')
                    traceback.print_exc()
                    return redirect(url_for('all_orders')) 

                if (current_user.id != orders.customer_id):
                    flash('Some thing went wrong while getting the order.','danger')
                    traceback.print_exc()
                    return redirect(url_for('all_orders'))  

                
                for _key, product in orders.orders.items():
                    discount= (product['discount'] / 100) * float(product['price']) 
                    subTotal += float(product['price']) * int(product['quantity'])
                    subTotal -= discount
                    grandTotal= float("%.8f" % (subTotal))

                brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
                categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all() 
                return render_template(
                    'customer/order.html', 
                    categories=categories,
                    brands=brands,
                    logged = current_user.is_authenticated, 
                    administrator=True if 'email' in session else False,  
                    grandTotal=grandTotal, 
                    customer=customer,
                    orders=orders
                )      

        except Exception as e:
            print(e)
            traceback.print_exc()
            flash('Some thing went wrong while getting the order.','danger')
            return redirect(url_for('all_orders'))
    
    @staticmethod
    def order_info(product_id):
        try:
            if current_user.is_authenticated:
                reference_product = AddProduct.query.filter_by(product_id=product_id).first()
                if reference_product.owner_email != current_user.email:
                    flash('Some thing went wrong.','danger')
                    return redirect(url_for('customer'))

                que= db.session.query(CustomerOrder,Register.name,Register.email,Register.country,Register.city,Register.address,Register.zipcode,Register.contact).\
                filter(CustomerOrder.customer_id==Register.id).\
                order_by(CustomerOrder.date_created.desc()).all()

                output_orders = []
                for i in range(len(que)):
                    if product_id in que[i][0].orders.keys():
                        local_product = {
                            "order": que[i][0],
                            "product": {**{"id": product_id}, **que[i][0].orders[product_id]},
                            "customer": {"name":que[i][1],"email":que[i][2],"country":que[i][3],"city":que[i][4],"address":que[i][5],"zipcode":que[i][6],"contact":que[i][7]}
                        }
                        output_orders.append(local_product)

                if (output_orders== []):
                    flash('The product has not been sold yet','warning')
                    return redirect(url_for('customer'))

                brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
                categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all() 
                possible_status = ["Pending","Processed","Shipped"]

                return render_template(
                    'customer/order_info.html', 
                    categories=categories, 
                    brands=brands, 
                    logged = current_user.is_authenticated, 
                    administrator=True if 'email' in session else False, 
                    orders=output_orders, 
                    reference_product=reference_product,
                    possible_status=possible_status)      
    
        except Exception as e:
            print(e)
            traceback.print_exc()
            flash('Some thing went wrong while getting the info.','danger')
            return redirect(url_for('customer'))

    @staticmethod
    def all_orders():
        try:
            if current_user.is_authenticated:
                customer_id= current_user.id
                orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.date_created.desc()).all()
                brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
                categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()

                return render_template(
                    'customer/all_orders.html', 
                    title='Customer Page', 
                    orders=orders, 
                    categories=categories, 
                    brands=brands, 
                    logged = current_user.is_authenticated, 
                    administrator=True if 'email' in session else False
                    )

        except Exception as e:
            print(e)
            traceback.print_exc()
            flash('Some thing went wrong while getting the orders.','danger')
            return redirect(url_for('customer'))
    
    @staticmethod
    def update_product_status(id):
        try:
            if current_user.is_authenticated:
                if request.method == 'POST':
                    product_id =request.form.get('product')
                    reference_product = AddProduct.query.filter_by(product_id=product_id).first()

                    if reference_product.owner_email != current_user.email:
                        flash('Some thing went wrong while getting the order.','danger')
                        return redirect(url_for('customer'))

                    order = CustomerOrder.query.filter_by(invoice=id).order_by(CustomerOrder.date_created.desc()).first()
                    
                    if str(product_id) in order.orders.keys():
                        order.orders[product_id]['status'] =request.form.get('status')
                        flag_modified(order, "orders")
                        db.session.add(order)
                        db.session.commit()
                    return redirect(url_for('order_info', product_id=product_id))
   
        except Exception as e:
            print(e)
            flash('Some thing went wrong while getting the order.','danger')
            return redirect(url_for('customer'))
    
    @staticmethod
    def profile():
        try:

            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            if current_user.is_authenticated:
                customer_id= current_user.id
                user_data = Register.query.filter_by(id=customer_id).first()

                return render_template(
                    'customer/profile.html', 
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

        except Exception as e:
            print(e)
            flash('Some thing went wrong.','danger')
            return redirect(url_for('customer'))