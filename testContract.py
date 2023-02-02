from contracts import DEX
from utils import debug_file

def checkbalance(test_dex,address, name):
    print("["+name+"] Remote wallet: ", test_dex.getRemoteBalance(address))
    print("["+name+"] Local  wallet: ", test_dex.getLocalBalance(address))



def get_product_info(test_dex,id):
    blockchain_id, price, amount, discount, owner, is_nft = test_dex.getProduct(id)

    print()
    print("Product id: ",id)
    print("Saved product id: ",blockchain_id)
    print("NFT: ", is_nft)
    print("Price: ", price)
    print("Amount: ", amount)
    print("Discount: ", discount)
    print("Owner: ", owner)
    print()

    return blockchain_id, price, amount, discount, owner, is_nft




def add_product(test_dex, seller, product):

 
    print("[Before AddProduct]")
    checkbalance(test_dex, seller, "seller")

    print()

    metadata = None
    if "metadata" in product.keys():
        metadata = product["metadata"]

    test_dex.addProduct(
        product['id'],
        product['price'],
        product['stock'],
        product['discount'],
        product['is_nft'],
        {"from": seller}, 
        metadata = metadata
    )
    print()

    print("[After AddProduct]")
    checkbalance(test_dex, seller, "seller")

    get_product_info(test_dex,product["id"])
    return 

def edit_product(test_dex, owner, product):
    
    print("[Before EditProduct]")
    checkbalance(test_dex, owner, "owner")

    print()
    metadata = None
    if "metadata" in product.keys():
        metadata = product["metadata"]
    test_dex.editProduct(
        product['id'],
        product['price'],
        product['stock'],
        product['discount'],
        {"from": seller}, 
        metadata = metadata
    )
    print()

    print("[After EditProduct]")
    checkbalance(test_dex, owner, "owner")
    get_product_info(test_dex,product["id"])

    return 


def buy_product(test_dex, buyer, seller, ids, amounts):

   

    print("[Before buyProduct]")
    checkbalance(test_dex, buyer, "Buyer")
    checkbalance(test_dex, seller, "Seller")

    print()
    ROI= test_dex.buyProducts(dict(zip(ids, amounts)), {"from": buyer})
    print()

    print("[After buyProduct]")
    checkbalance(test_dex, buyer, "Buyer")
    checkbalance(test_dex, seller, "Seller")
    return ROI




def delete_product(test_dex, owner, product_id):


    print("[Before DeleteProduct]")
    checkbalance(test_dex, owner, "owner")

    print()
    test_dex.deleteProduct(product_id, {"from": owner})
    print()

    print("[After DeleteProduct]")
    checkbalance(test_dex, owner, "owner")
   

    return 


def withdraw(test_dex, address, value, caller = "address"):
    

    print("[Before withdraw]")
    checkbalance(test_dex, address, caller)
    checkbalance(test_dex, test_dex.contract_address, "DEX Contract")

    print()
    test_dex.withdraw(value,{"from": address})
    print()
    

    print("[After withdraw]")
    checkbalance(test_dex, address, caller)
    checkbalance(test_dex, test_dex.contract_address, "DEX Contract")


if __name__ == "__main__":
    test_dex = DEX.load(debug = True)

    buyer = list(debug_file.keys())[0]
    seller = list(debug_file.keys())[1]

    print("ERC20  address:", test_dex.getTokenAddress())
    print("ERC721 address:", test_dex.getTokenNftAddress())
    print("DEX address:", test_dex.contract_address)

    print()
    print()
    print()
    test_dex.token_nft.setApprovalForAll(test_dex.contract_address,True, {"from":seller})
    test_dex.token_nft.setApprovalForAll(test_dex.contract_address,True, {"from":buyer})


    product1={
        "id":"Prod1",
        "price": test_dex.toWei(1), 
        "is_nft":True, 
        "metadata": "123456abcdef",
        "stock":1, 
        "discount":1
    }

    product2={
        "id":"Prod2",
        "price": test_dex.toWei(1), 
        "is_nft":False, 
        "stock":2,
        "discount":0
    }
    
    add_product(test_dex, seller, product1)
    add_product(test_dex, seller, product2)


    uri1 = test_dex.token_nft.getURI(product1["id"])
    print("URI NFT: ",uri1)


    product1["price"]=test_dex.toWei(2)
    product2["discount"]= 1
    

    edit_product(test_dex, seller, product1)
    edit_product(test_dex, seller, product2)

    amounts={product1["id"]:1, product2["id"]:1}


    checkbalance(test_dex, test_dex.contract_address, "DEX Contract")



    ROI=buy_product(
        test_dex, 
        buyer, 
        seller, 
        [product1["id"],product2["id"]], 
        [amounts[product1["id"]],amounts[product2["id"]]]
    )

    get_product_info(test_dex,product1["id"])
    get_product_info(test_dex,product2["id"])

    print("ROI: ",ROI) 
    withdraw(
        test_dex, 
        seller, 
        ROI, 
        caller = "seller"
    )

    # delete_product(test_dex,seller,product2["id"])
    get_product_info(test_dex,product2["id"])

