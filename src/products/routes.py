
from flask import redirect, render_template, url_for, flash, jsonify, send_file, abort
from flask import request, session, current_app
from flask_login import current_user

from .models import Brand, Category, AddProduct
from .forms import Addproducts
from src.customers import Register
from utils import db, photos
from utils import dex_contract, dex_instance, tmp_nft, image_complete_path, token_nft_contract

import traceback
import secrets, os, hashlib
import base64

class ProductManager:

    @staticmethod
    def home():
        # _= request.args.get('q')
        page= request.args.get('page', 1, type=int)
        products= AddProduct.query.filter(AddProduct.stock > 0)\
            .paginate(page=page, per_page= 8)
        
        categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
        brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
        return render_template(
            'products/showcase.html',
            url='home',
            search="",
            products=products,
            brands=brands,
            categories=categories,
            logged = current_user.is_authenticated, 
            administrator=True if 'email' in session else False,
            contract_info = {
                "abi": dex_contract["abi"],
                "address": dex_contract["address"]
            })

    @staticmethod
    def result():
        try:
            searchword= request.args.get('q')
            page= request.args.get('page', 1, type=int)

            if searchword == "":             
                products= AddProduct.query.filter(AddProduct.stock > 0)\
                    .paginate(page=page, per_page= 8)
            else:
                products= AddProduct.query\
                    .msearch(searchword, fields=['name', 'desc'])\
                    .filter(AddProduct.stock > 0)\
                    .paginate(page=page, per_page= 8)\
                
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()

            return render_template(
                'products/showcase.html', 
                url='result', 
                search=searchword, 
                products=products, 
                brands=brands, 
                categories=categories, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                }) 
        except:
            return redirect(url_for('home'))

    @staticmethod
    def get_brand():
        try:
            id= request.args.get('q')
            page= request.args.get('page', 1, type=int)
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            get_b= Brand.query.filter_by(id=id).first_or_404()
            get_brand_prod= AddProduct.query.filter_by(brand=get_b).filter(AddProduct.stock > 0).paginate(page=page, per_page=8)
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()

            return render_template(
                'products/showcase.html', 
                url='get_brand', 
                search=id, 
                products=get_brand_prod, 
                brands=brands, 
                categories=categories, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                })      
        except:
            return redirect(url_for('home'))

    @staticmethod
    def get_category():
        try:
            id= str(request.args.get('q'))
            page= request.args.get('page', 1, type=int)
            get_c= Category.query.filter_by(id=id).first_or_404()
            get_cat_prod= AddProduct.query.filter_by(category=get_c).filter(AddProduct.stock > 0).paginate(page=page, per_page= 8)
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()

            return render_template(
                'products/showcase.html', 
                url='get_category', 
                search=id, 
                products=get_cat_prod, 
                categories=categories, 
                brands=brands, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                })
        except:
            return redirect(url_for('home'))

    @staticmethod
    def get_product(id):
        try: 
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            product = AddProduct.query.filter_by(product_id=id).first()

            return render_template(
                'products/product.html', 
                product=product, 
                brands=brands, 
                categories=categories, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                        "abi": dex_contract["abi"],
                        "address": dex_contract["address"]
                    }
                )
        except:
            flash("No product found","warning")
            return redirect(url_for('home'))

    @staticmethod
    def addbrand():
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))

        if request.method== 'POST':
            getbrand= request.form.get('brand')
            brand= Brand(name=getbrand)
            db.session.add(brand)
            flash(f'The brand {getbrand} was added to your database.', 'success')
            db.session.commit()
            return redirect(url_for('brands'))

        return render_template(
            'products/addbrand.html', 
            brands='brands' , 
            administrator=True if 'email' in session else False
            )

    @staticmethod
    def updatebrand(id):
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
            
        updatebrand= Brand.query.get_or_404(id) 
        brand= request.form.get('brand')

        if request.method== 'POST':
            updatebrand.name= brand
            flash(f'Your brand has been updated.','success')
            db.session.commit()
            return redirect(url_for('brands'))

        return render_template(
            'products/updatebrand.html', 
            title='Update brandy page', 
            updatebrand=updatebrand, 
            administrator=True if 'email' in session else False
            )            

    @staticmethod
    def deletebrand(id):
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))

        try:
            brand= Brand.query.filter_by(id=id).first()
            db.session.delete(brand)
            db.session.commit()
            flash(f'The brand {brand.name} was deleted from your database.', 'success')
        except:
            flash(f'An error ocurred','danger')    
        return redirect(url_for('brands'))
    
    @staticmethod
    def addcat():
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
            
        if request.method== 'POST':
            getcat= request.form.get('category')
            cat= Category(name=getcat)
            db.session.add(cat)
            flash(f'The category {getcat} was added to your database.', 'success')
            db.session.commit()
            return redirect(url_for('categories'))
        return render_template('products/addbrand.html', administrator=True if 'email' in session else False)
    
    @staticmethod
    def updatecat(id):
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
            
        updatecat= Category.query.get_or_404(id)
        category= request.form.get('category')

        if request.method== 'POST':
            updatecat.name= category
            flash(f'Your category has been updated.','success')
            db.session.commit()
            return redirect(url_for('categories'))
        return render_template('products/updatebrand.html', title='Update category page', updatecat=updatecat, administrator=True if 'email' in session else False)            

    @staticmethod
    def deletecat(id):
        if 'email' not in session:
            flash(f'Please login first', 'danger')
            return redirect(url_for('login'))
            
        category= Category.query.filter_by(id=id).first()
        try:
            db.session.delete(category)
            db.session.commit()
            flash(f'The category {category.name} was deleted from your database.', 'success')
        except:
            flash(f'An error ocurred','danger')    
        return redirect(url_for('categories'))


    @staticmethod
    def addproduct():
        product_id = secrets.token_hex(16)
        try:
            if not current_user.is_authenticated:
                flash(f'Please login first', 'danger')
                return redirect(url_for('customer_login'))
                
            brands= Brand.query.all()
            categories= Category.query.all()
            form= Addproducts(request.form)

            if request.method =='POST':
                email = current_user.email
                myself= Register.query.filter_by(email=email).first()
          
                product_id = request.form.get('product_id')
                blockchain_info = dex_instance["value"].getProduct(product_id)

                name= form.name.data
                
                price=dex_instance["value"].downscaleETH(blockchain_info[1])# form.price.data
                discount=blockchain_info[3]# form.discount.data
                stock=blockchain_info[2]# int(form.stock.data)
                desc= form.description.data
                brand= request.form.get('brand')
                category= request.form.get('category')
                is_nft =blockchain_info[-1]# False

                image_1 = None
                image_2 = None
                image_3 = None
                nft_hash = None

                if is_nft == False:
                    image_1 = request.files.get('image_1')
                else:
                    token_nft_uri = dex_instance["value"].token_nft.getURI(product_id)
                    token_nft_meta = token_nft_uri.split("meta=")[1]    
                    nft_hash = token_nft_meta

                    assert nft_hash in tmp_nft.keys()

                    image_content_type = tmp_nft[nft_hash].split(";")[0].split(":")[1]
                    image_type = image_content_type.split("/")[1]
                    image_1 = product_id + "."+image_type
                    complete_path = os.path.join(image_complete_path["value"], image_1)

                    with open(complete_path, "wb") as f:
                        base64_content = tmp_nft[nft_hash].split("base64,")[1]
                        f.write(base64.b64decode(base64_content))
                    
                    del tmp_nft[nft_hash]

                if is_nft == False:
                    image_1=photos.save(image_1, name=product_id + "_1" + '.')

                    image_2 = request.files.get('image_2')
                    if image_2.filename != "":
                        image_2=photos.save(image_2, name=product_id + "_2" + '.')
                    else:
                        image_2 = None

                    image_3 = request.files.get('image_3')
                    if image_3.filename != "":
                        image_3=photos.save(image_3, name=product_id + "_2" + '.')
                    else:
                        image_3 = None

 
                remoteAddress = blockchain_info[4]
                # _,_,_,_,remoteAddress,_ = dex_instance["value"].getProduct(product_id)
                remoteAddress = dex_instance["value"].Web3.toChecksumAddress(remoteAddress)

                


                addpro= AddProduct(
                    name=name,
                    price=price,
                    discount=discount, 
                    stock=stock, 
                    desc=desc, 
                    brand_id=brand, 
                    # owner_id=myself.id, 
                    owner_address=remoteAddress,
                    owner_email= myself.email,
                    category_id=category, 
                    image_1=image_1, 
                    image_2=image_2, 
                    image_3=image_3, 
                    product_id= product_id,
                    is_nft = is_nft,
                    nft_hash=nft_hash
                )
                db.session.add(addpro)
                flash(f'The product {name} has been added to your database.', 'success')
                db.session.commit()

                return redirect(url_for('customer'))
                
            return render_template(
                'products/addproduct.html' , 
                title='Add product page', 
                form=form, 
                brands=brands, 
                categories=categories, 
                product_id = product_id,
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                }
            )    

        except Exception as e:
            print(e)
            print(traceback.print_exc())
            flash(f'Something went wrong.', 'danger')
            return render_template(
                'products/addproduct.html' , 
                title='Add product page', 
                form=form, brands=brands, 
                categories=categories, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                },
                product_id = product_id
            )   

    @staticmethod
    def updateproduct(id):
        try: 
            if not current_user.is_authenticated:
                flash(f'Please login first', 'danger')
                return redirect(url_for('customer_login'))
                
            brands= Brand.query.all()
            categories= Category.query.all()
            product= AddProduct.query.get_or_404(id)
            brand= request.form.get('brand')
            category= request.form.get('category')
            form= Addproducts(request.form)
         

            if request.method == 'POST':
                blockchain_info = dex_instance["value"].getProduct(id)

                product.name= form.name.data
                product.price=dex_instance["value"].downscaleETH(blockchain_info[1])# form.price.data
                product.discount=blockchain_info[3]# form.discount.data
                product.stock=blockchain_info[2]# int(form.stock.data)
                product.brand_id= brand
                product.category_id= category
                product.desc= form.description.data
                product.is_nft =blockchain_info[-1]# False


                if product.is_nft:
                    token_nft_uri = dex_instance["value"].token_nft.getURI(id)
                    token_nft_meta = token_nft_uri.split("meta=")[1]    
                    nft_hash = token_nft_meta

                    if request.files.get("image_1") and request.files.get("image_1").filename != "":
                        assert nft_hash in tmp_nft.keys()
            
                        try:
                            os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_1))
                        except:
                            pass
                        finally:
                            image_content_type = tmp_nft[nft_hash].split(";")[0].split(":")[1]
                            image_type = image_content_type.split("/")[1]
                            image_1 = id + "."+image_type
                            complete_path = os.path.join(image_complete_path["value"], image_1)

                            with open(complete_path, "wb") as f:
                                base64_content = tmp_nft[nft_hash].split("base64,")[1]
                                f.write(base64.b64decode(base64_content))

                            product.image_1 = image_1
                            product.nft_hash=nft_hash

                            del tmp_nft[nft_hash]
                
                if product.is_nft == False:
                    if request.files.get('image_1').filename != "":
                        try:
                            os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_1))  
                            product.image_1=  photos.save(request.files.get('image_1'), name=id + "_1" + '.')  
                        except:
                            product.image_1=  photos.save(request.files.get('image_1'), name=id + "_1" + '.')

                    if request.files.get('image_2').filename != "":
                        try:
                            os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_2))  
                            product.image_2=  photos.save(request.files.get('image_2'), name=id + "_2" + '.')  
                        except:
                            product.image_2=  photos.save(request.files.get('image_2'), name=id + "_2" + '.')  

                    if request.files.get('image_3').filename != "":
                        try:
                            os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_3))  
                            product.image_3=  photos.save(request.files.get('image_3'), name=id + "_3" + '.')  
                        except:
                            product.image_3=  photos.save(request.files.get('image_3'), name=id + "_3" + '.')  

                db.session.commit()
                flash(f'You product has been updated.', 'success')
                return redirect(url_for('customer'))

            form.name.data= product.name
            form.price.data= product.price
            form.discount.data= product.discount
            form.stock.data= product.stock
            form.description.data= product.desc

            return render_template(
                'products/updateproduct.html', 
                form=form, 
                product=product, 
                brands=brands, 
                categories=categories, 
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
            flash(f'Something went wrong.', 'danger')

            return render_template(
                'products/updateproduct.html', 
                form=form, 
                product=product, 
                brands=brands, 
                categories=categories, 
                logged = current_user.is_authenticated, 
                administrator=True if 'email' in session else False,
                contract_info = {
                    "abi": dex_contract["abi"],
                    "address": dex_contract["address"]
                }
            )    


    @staticmethod
    def deleteproduct(id):
        try:
            if current_user.is_authenticated or ('email' in session):   
                product= AddProduct.query.filter_by(product_id=id).first()
                try:
                    os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_1))

                    if product.image_2 != None:
                        os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_2))
                    if product.image_3 != None:  
                        os.unlink(os.path.join(current_app.root_path, 'static','images', product.image_3))  

                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    flash(f'An error ocurred.','danger')    

                db.session.delete(product)
                db.session.commit()
                flash(f'The product {product.name} was deleted from your database.', 'success')
                if current_user.is_authenticated:
                    return redirect(url_for('customer'))
                if ('email' in session):
                    return redirect(url_for('admin'))

            else:
                flash(f'Please login first', 'danger')
                return redirect(url_for('customer_login'))

                
        except Exception as e:
            print(e)
            traceback.print_exc()
            return redirect(url_for('home'))

    def nftMetadata():
        try:
            # _ = request.args.get("id")
            nft_hash = request.args.get("meta")
            product = AddProduct.query.filter_by(nft_hash=nft_hash).first()
            if product.is_nft:
                filename = os.path.join(image_complete_path["value"],product.image_1) 
                return send_file(filename, mimetype="image/"+filename.split(".")[-1])
                
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            
        flash(f'NFT not found','info')
        return redirect(url_for('home'))
    
    def temporary():
        try:
            if request.method== 'POST':
                id = request.form.get("id")
                blob = request.form.get("blob")
                
                if blob != None and blob != "":

                    metadata = blob.split("base64,")[1].encode("utf-8")
                    metadata = hashlib.md5(metadata).digest()

                    # print("MD5 output: ", metadata)
                    metadata = metadata.hex().rstrip("0")

                    if len(metadata) % 2 != 0:
                        metadata = metadata + '0'
                    # print("MD5 output adjusted: ", metadata)
                    nft_hash=""+id+""+metadata    
                    # print("nft hash pre",nft_hash)
                    # print("nft hash pre1",nft_hash.encode("utf-8"))

                    nft_hash = "0x"+dex_instance["value"].getHash(nft_hash.encode("utf-8"))
                    # print("nft hash", nft_hash)
                    tmp_nft[nft_hash] = blob

                else:
                    return "No image uploaded"
                return "Success"

            return "get"
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            flash(f'Error in temporary','danger')
            return redirect(url_for('home'))