from flask import Flask, session
from flask_uploads import configure_uploads
from flask_migrate import Migrate
from flask_login import login_required, current_user, logout_user, login_user
from argparse import ArgumentParser

from src import *
from contracts import DEX

from utils import db, bcrypt, search, login_manager, photos
from utils import dex_contract, dex_instance, basedir, image_complete_path
from utils import server_data, admin_info
from utils import web3_protocol, web3_domain, web3_uri, web3_port, web3_uri, networkID

import os

basedir["value"] = os.path.abspath(os.path.dirname(__file__))
image_complete_path["value"] = os.path.join(basedir["value"],"static","images")
app= Flask(__name__)

app.config['SECRET_KEY']='dsadsadsa'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

app.config['UPLOADED_PHOTOS_DEST']= image_complete_path["value"]

configure_uploads(app, photos)

migrate= Migrate(app, db)

with app.app_context():

    db.init_app(app)
    db.create_all()

    bcrypt.init_app(app)
    search.init_app(app)
    
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)    

    login_manager.init_app(app)
    login_manager.login_view='customer_login'
    login_manager.needs_refresh_message_category='danger'
    login_manager.login_message= u'Please login first'


### Admin Managment

@app.route('/admin')
def admin():
    return AdminManager.admin()

@app.route('/admin/update/', methods=['GET', 'POST'])
def admin_update():
    return AdminManager.admin_update()

@app.route('/admin/brand')
def brands():
    return AdminManager.brands()

@app.route('/admin/category')
def categories():
    return AdminManager.categories()

@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    return AdminManager.register()

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    return AdminManager.login()

@app.route('/admin/logout')
def logout():
    return AdminManager.logout()

@app.route('/admin/profile')
def admin_profile():
    return AdminManager.profile()

### CartManagement

@app.route('/cart/add', methods=['POST'])
def addcart():
    return CartManager.addcart()

@app.route('/cart')
@login_required
def getcart():
    return CartManager.getcart()

@app.route('/cart/empty')
def emptycart():
    return CartManager.emptycart()

@app.route('/cart/update/<code>', methods=['POST'])
def updatecart(code):
    return CartManager.updatecart(code)

@app.route('/cart/deleteitem/<id>')
def deleteitem(id):
    return CartManager.deleteitem(id)

@app.route('/cart/clear')
def clearcart():
    return CartManager.clearcart()

### Customer managment

@app.route('/customer')
def customer():
    return CustomerManager.customer()

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    return CustomerManager.customer_register()

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    return CustomerManager.customer_login()

@app.route('/customer/logout')
def customer_logout():
    return CustomerManager.customer_logout()


@app.route('/customer/update/', methods=['GET', 'POST'])
def customer_update():
    return CustomerManager.customer_update()

@app.route('/customer/delete/', methods=['GET', 'POST'])
@login_required
def customer_delete():
    return CustomerManager.customer_delete()

@app.route('/customer/buy')
@login_required
def getorder():
    return CustomerManager.getorder()

@app.route('/customer/order/<invoice>')
@login_required
def orders(invoice):
    return CustomerManager.orders(invoice)

@app.route('/customer/my_orders')
@login_required
def all_orders():
    return CustomerManager.all_orders()

@app.route('/customer/profile')
@login_required
def profile():
    return CustomerManager.profile()

@app.route('/customer/order_info/<product_id>')
@login_required
def order_info(product_id):
    return CustomerManager.order_info(product_id)

@app.route('/customer/update_product_status/<id>',methods=['GET', 'POST'])
@login_required
def update_product_status(id):
    return CustomerManager.update_product_status(id)
'''
@app.route('/customer/get_pdf/<invoice>')
@login_required
def get_pdf(invoice):
    return CustomerManager.get_pdf(invoice)
'''
### Product Manager

@app.route('/')
@app.route('/showcase')
def home():
    return ProductManager.home()

@app.route('/showcase/result')
def result():
    return ProductManager.result()

@app.route('/showcase/brand/')
def get_brand():
    return ProductManager.get_brand()

@app.route('/showcase/category/', methods = ["GET"])
def get_category():
    return ProductManager.get_category()

@app.route('/showcase/product/<id>')
def get_product(id):
    return ProductManager.get_product(id)

@app.route('/admin/brand/add', methods=['GET', 'POST'])
def addbrand():
    return ProductManager.addbrand()

@app.route('/admin/brand/update/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    return ProductManager.updatebrand(id)

@app.route('/admin/brand/delete/<int:id>')
def deletebrand(id):
    return ProductManager.deletebrand(id)

@app.route('/admin/category/add', methods=['GET', 'POST'])
def addcat():
    return ProductManager.addcat()

@app.route('/admin/category/update/<int:id>', methods=['GET', 'POST'])
def updatecat(id):
    return ProductManager.updatecat(id)

@app.route('/admin/category/delete/<int:id>')
def deletecat(id):
    return ProductManager.deletecat(id)

@app.route('/customer/product/add', methods=['GET', 'POST'])
@login_required
def addproduct():
    return ProductManager.addproduct()

@app.route('/customer/product/update/<id>', methods=['GET', 'POST'])
@login_required
def updateproduct(id):
    return ProductManager.updateproduct(id)

@app.route('/customer/product/delete/<id>')
# @login_required
def deleteproduct(id):
    return ProductManager.deleteproduct(id)

@app.route('/'+server_data["api"]+'/')
def nftMetadata():
    return ProductManager.nftMetadata()

@app.route('/temporary/', methods = ["POST"])
@login_required
def temporary():
    return ProductManager.temporary()

def buildParser():
    parser=ArgumentParser()

    parser.add_argument("-web3-protocol",dest="web3_protocol", type=str, default=web3_protocol)
    parser.add_argument("-web3-host",dest="web3_host", type=str, default=web3_domain)
    parser.add_argument("-web3-port",dest="web3_port", type=str, default=web3_port)

    parser.add_argument("-blockchain-networkId",dest="networkID", type=int, default=networkID["value"])
    
    return parser

def set_params():
    global server_protocol, server_host, server_port
    global web3_uri, networkID

    parser = buildParser()
    args = parser.parse_args()

    default_web3_uri = web3_uri["value"]
    default_networkID = networkID["value"]

    dex_instance["value"] = DEX.load()

    try:

        web3_uri["value"] = args.web3_protocol.lower() + "://" + \
            args.web3_host.lower() + ":" + \
            args.web3_port.lower()

        networkID["value"] = args.networkID

    except Exception as e:
        print(e)
        print("[Warning] Using default settings")

        web3_uri["value"] = default_web3_uri
        networkID["value"] = default_networkID

    protocol, domain, port, api = dex_instance["value"].token_nft.getServerData()

    if protocol != server_data["protocol"] or \
        domain != server_data["host"] or \
            port != str(server_data["port"]) or \
                api != server_data["api"]:

        print("[Warning] Server data are different from the ones in the blockchain")
        
        dex_instance["value"].token_nft.setServerData(
            server_data["protocol"], 
            server_data["host"], 
            server_data["port"], 
            server_data["api"],
            admin_info["private_key"],
            {
                "from": admin_info["address"]
            })

        print("[Info] New server data has been updated in the blockchain")

    # print("NETWORK_ID", networkID["value"])

if __name__ == '__main__':
    
    set_params()
    # dex_contract["instance"] = DEX()
    # for k,v in dex_contract.items():
    #     print(f"{k} -> {v}")
    #     print()

    # dex_instance = DEX.at(dex_contract["address"])

    # print(f"address: {dex_instance.contract_address}")
    # print(f"abi: {dex_instance.contract_abi}")
    print()
    print()
    # print("SERVER URI: ", server_protocol["value"],"://",server_host["value"],":",server_port["value"])
    app.run(
        host=server_data["host"], 
        port=server_data["port"], 
        debug=False)
    