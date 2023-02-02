from flask import redirect, render_template, url_for, flash, request, session

from src.products.models import AddProduct
from src.products.routes import *
from utils import dex_contract, token_contract
import collections
import traceback

class CartManager:
    
    @staticmethod
    def MergeDicts(dict1, dict2):
        if isinstance(dict1, list) and isinstance(dict2, list):
            return dict1 + dict2
        elif isinstance(dict1, dict) and isinstance(dict2, dict):
            return dict(list(dict1.items()) + list(dict2.items()))
        return False

    @staticmethod
    def addcart():
        try:
            product_id = request.form.get('product_id')
            quantity = request.form.get('quantity')
            product = AddProduct.query.filter_by(product_id=product_id).first()
            if product_id and quantity and request.method=='POST':
                
                DictItems = {product_id: {'quantity': quantity}}
                qnt = DictItems[product_id]['quantity']
     
                assert int(qnt) <= int(product.stock)

  
                if 'Shoppingcart' in session:
                    if product_id in session['Shoppingcart']:
                        for key, item in session['Shoppingcart'].items():
                            if key == product_id:
                                
                                qnt = int(item['quantity'])
                                qnt += int(quantity)
                                
                                assert int(qnt) <= int(product.stock)
                                item['quantity'] = qnt
                                session.modified = True 
                    else:
                        session['Shoppingcart'] = CartManager.MergeDicts(session['Shoppingcart'], DictItems)
                        session.modified = True 
                        return redirect(request.referrer)
                else:
                    session['Shoppingcart'] = DictItems
                    session.modified = True 
                    return redirect(request.referrer)
        except Exception as e:
            print(e)
            traceback.print_exc()
        finally:
            return redirect(request.referrer)

    @staticmethod
    def getcart():
        trigger_stack_trace = True
        try:

            brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()

            if 'Shoppingcart' not in session or len(session['Shoppingcart']) <=0:
                return redirect(url_for('clearcart'))

            subtotal=0
            total=0    
            DictItems ={}

            shop_key = list(session['Shoppingcart'].keys())
            for key in shop_key:
                value = session['Shoppingcart'][key]
                product = AddProduct.query.filter_by(product_id=key).first()
                if product==None:
                    session['Shoppingcart'].pop(key, None)
                    session.modified = True
                    if len(session['Shoppingcart'].keys())==0:
                        flash(f"Cart is empty", "warning")
                        trigger_stack_trace = False
                        raise Exception("Shoppingcart is empty")  

      
                else:
                    item = {str(key): {
                    'discount': product.discount, 'image_1': product.image_1, 'name': product.name, 'price':float(product.price), 
                    'quantity':session['Shoppingcart'][str(key)]['quantity'], 'stock':product.stock, 'product_id':product.product_id, "is_nft":product.is_nft}}

                    item1 = {str(key):{**product.as_dict_type(), **{'quantity':session['Shoppingcart'][str(key)]['quantity']}}}


                    DictItems = CartManager.MergeDicts(DictItems,item1)


                    discount= (product.discount/100) * float(product.price)
                    subtotal+= float(product.price) * int(value['quantity'])
                    subtotal -= discount
                    total= float("%.8f" % (subtotal))

            return render_template(
                'products/cart.html',
                total=total, 
                products = DictItems,
                categories = categories,
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
                }
            )    
        except Exception as e:
            if trigger_stack_trace:
                print(e)
                traceback.print_exc()
            return redirect(url_for('clearcart'))   

               
    @staticmethod
    def emptycart():
        brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
        categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()

        return render_template(
            'products/cartclear.html', 
            categories=categories, 
            brands=brands, 
            logged = current_user.is_authenticated, 
            administrator=True if 'email' in session else False
            )
    
    @staticmethod
    def updatecart(code):
        if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
            return redirect(url_for('cartclear'))
        if request.method == 'POST':
            quantity= request.form.get('quantity')
            try:
                for key, item in session['Shoppingcart'].items():
                    product = AddProduct.query.filter_by(product_id=key).first()
                    if key == code:
                        assert int(quantity) <= int(product.stock)
                        item['quantity']= quantity
                        
                        session.modified= True
                        flash('Item is updated.')
                        return redirect(url_for('getcart'))      
            except Exception as e:
                print(e)
                traceback.print_exc()
                return redirect(url_for('getcart'))      

    @staticmethod
    def deleteitem(id):
        if 'Shoppingcart' not in session and len(session['Shoppingcart']) <= 0:
            return redirect(url_for('cartclear'))
        try:
      
            for key in session['Shoppingcart'].keys():
                if key== id:
                    session['Shoppingcart'].pop(key, None)
                    session.modified = True
                    return redirect(url_for('getcart'))     
        except Exception as e:
            print(e)
            traceback.print_exc()
            return redirect(url_for('getcart'))        

    @staticmethod
    def clearcart():
        try:
            # brands= Brand.query.join(AddProduct, (Brand.id==AddProduct.brand_id)).all()
            # categories= Category.query.join(AddProduct, (Category.id==AddProduct.category_id)).all()
            session.pop('Shoppingcart', None)
            session.modified = True
            return redirect(url_for('emptycart'))
        except Exception as e:
            print(e)    
            traceback.print_exc()
            return redirect(url_for('home'))
            