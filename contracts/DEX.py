from Crypto.Hash import keccak

from .ContractWrapper import ContractWrapper
from .ERC20Token import ERC20Token
from .ERC721Token import ERC721Token
from utils import StorageHandler
from utils import web3_uri, server_data
from utils import dex_contract, token_contract, token_nft_contract

class DEX(ContractWrapper):
    def __init__(self, debug = False):

        super(DEX, self).__init__("DEX", web3_uri["value"], debug = debug)
        self.token = None
        self.token_nft = None

        self.function_structure = {}

        # self.add_params = "(string,uint256,uint256,uint256)"
        # self.add_nft_params = "(string,uint256,uint256,uint256,string)"

    def getHash(self,txt):
        hash_manager = keccak.new(digest_bits=256)
        hash_manager.update(txt)
        return hash_manager.hexdigest()


    def publish_contract(self, initialSupply = 100):
        interfaces = self.compile_contract("ERC20Token", "ERC721Token", compiled_files=["ERC20Token","ERC721Token"])
        #interfaces = self.compile_contract("ERC20Token", compiled_files=["ERC20Token"])
        
        self.deploy_contract(
            interfaces["DEX"], 
            initialSupply, 
            server_data["protocol"], 
            server_data["host"], 
            str(server_data["port"]), 
            server_data["api"]
        )

        self.setFunctionsStructure()

        contract_data = {
            "address": self.contract_address,
            "abi": self.contract_abi
        }

        token_data = {
            "address": self.getTokenAddress(),
            "abi": interfaces["ERC20Token"]["abi"]
        }
        
        token_nft_data = {
            "address": self.getTokenNftAddress(),
            "abi": interfaces["ERC721Token"]["abi"]
        }
        

        StorageHandler.save_contract(contract_data, "DEX")
        StorageHandler.save_contract(token_data, "ERC20Token", super_contract="DEX")
        StorageHandler.save_contract(token_nft_data, "ERC721Token", super_contract="DEX")

        self.token = ERC20Token(token_data["address"], token_data["abi"], debug = self.debug)
        self.token_nft = ERC721Token(token_nft_data["address"], token_nft_data["abi"], debug = self.debug)

    def setFunctionsStructure(self):
        funcs_std = ["increaseSupply", "decreaseSupply", "deposit", "withdraw", "deleteProduct", "buyProducts"]

        for fun in funcs_std:
            FUN_str = str(self.contract.get_function_by_name(fun))
            self.function_structure[fun] = "("+FUN_str.split("(")[1].split(")")[0]+")"

        self.function_structure["addProductNoNft"] = "(string,uint256,uint256,uint256)"
        self.function_structure["addProductYesNft"] = "(string,uint256,uint256,uint256,string)"

        self.function_structure["editProductNoNft"] = "(string,uint256,uint256,uint256)"
        self.function_structure["editProductYesNft"] = "(string,uint256,uint256,uint256,string)"

    @staticmethod
    def load(debug = False):
        contract_dex = DEX(debug = debug)

        contract_dex.contract_address = dex_contract["address"]
        contract_dex.contract_abi = dex_contract["abi"]

        contract_dex.contract = contract_dex.Web3.eth.contract(
            address=contract_dex.contract_address, 
            abi=contract_dex.contract_abi 
        )

        contract_dex.setFunctionsStructure()

        contract_dex.token = ERC20Token(token_contract["address"], token_contract["abi"], debug = debug)
        contract_dex.token_nft = ERC721Token(token_nft_contract["address"], token_nft_contract["abi"], debug = debug)

        return contract_dex
        
    def upscaleETH(self, amount):
        if self.token != None:
            return int(amount * (10**self.token.contract.functions.decimals().call()))
        return int(self.toWei(amount))

    def downscaleETH(self, amount):
        if self.token != None:
            return amount / (10**self.token.contract.functions.decimals().call()) 
        return self.fromWei(amount)

    def getTokenAddress(self):
        return str(self.contract.functions.getToken().call())

    def getTokenNftAddress(self):
        return str(self.contract.functions.getTokenNft().call())

    def getLocalBalance(self, address):
        return self.contract.functions.getBalance(address).call()


    def increaseSupply(self, amount, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert type(amount) == int or type(amount) == float
        assert amount > 0

        amount = self.upscaleETH(amount)
        private_key = self.get_private_key(tx_dict["from"])
        self.BuildandSignTX(
            tx_dict["from"], 
            "increaseSupply", 
            private_key, 
            self.function_structure["increaseSupply"], 
            tx_dict, 
            amount
        )

    def decreaseSupply(self, amount, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert type(amount) == int or type(amount) == float
        assert amount > 0

        amount = self.upscaleETH(amount)
        private_key = self.get_private_key(tx_dict["from"])
        self.BuildandSignTX(
            tx_dict["from"], 
            "decreaseSupply", 
            private_key, 
            self.function_structure["decreaseSupply"], 
            tx_dict, 
            amount
        )

    def deposit(self,tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert "value" in tx_dict.keys()

        private_key = self.get_private_key(tx_dict["from"])
        self.BuildandSignTX(
            tx_dict["from"], 
            "deposit", 
            private_key, 
            self.function_structure["deposit"], 
            tx_dict
        )

    def withdraw(self, amount, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert amount - int(amount) == 0

        amount = int(amount) 

        private_key = self.get_private_key(tx_dict["from"])
        self.token.increaseAllowance(self.contract_address, amount, tx_dict)

        # allowance = self.contract.functions.getAllowance(tx_dict["from"], self.contract_address).call()
        # print("Allowance [account => contract]: ", allowance)

        self.BuildandSignTX(
            tx_dict["from"], 
            "withdraw", 
            private_key, 
            self.function_structure["withdraw"],
            tx_dict, 
            amount
        )
    
    def addProduct(self, id, price, amount, discount, is_nft,  tx_dict, metadata = None):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert type(is_nft) == bool

        assert type(amount) == int
        assert amount >= 0
        assert price - int(price) == 0
        assert price >= 0
        assert type(discount) == int
        assert discount >= 0
        assert metadata is None or type(metadata) == str
        assert is_nft == False or metadata is not None

        price = int(price)
        private_key = self.get_private_key(tx_dict["from"])

        if is_nft == False:
            self.BuildandSignTX(
                tx_dict["from"], 
                "addProduct", 
                private_key, 
                self.function_structure["addProductNoNft"], 
                tx_dict, 
                id, 
                price, 
                amount, 
                discount
            )
        else:
            self.BuildandSignTX(
                tx_dict["from"], 
                "addProduct", 
                private_key, 
                self.function_structure["addProductYesNft"], 
                tx_dict, 
                id, 
                price, 
                amount, 
                discount, 
                metadata
            )

    def getProduct(self, id):
        return self.contract.functions.getProduct(id).call()

    def editProduct(self, id, price, amount, discount, tx_dict, metadata = None):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts

        assert type(price) == int
        assert price >= 0

        assert type(amount) == int
        assert amount >= 0

        assert type(discount) == int
        assert discount >= 0

        assert metadata is None or type(metadata) == str

        is_nft = self.getProduct(id)[-1]

        assert is_nft == False or metadata is not None

        private_key = self.get_private_key(tx_dict["from"])
        print("editproduct", tx_dict["from"])
        
        if metadata is None:
            self.BuildandSignTX(
                tx_dict["from"], 
                "editProduct", 
                private_key,
                self.function_structure["editProductNoNft"], 
                tx_dict, 
                id, 
                price,
                amount,
                discount
            )
        else:
            self.BuildandSignTX(
                tx_dict["from"], 
                "editProduct", 
                private_key,
                self.function_structure["editProductYesNft"], 
                tx_dict, 
                id, 
                price,
                amount,
                discount,
                metadata
            )
    def deleteProduct(self, id, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts

        private_key = self.get_private_key(tx_dict["from"])

        self.BuildandSignTX(
            tx_dict["from"], 
            "deleteProduct", 
            private_key,
            self.function_structure["deleteProduct"], 
            tx_dict, 
            id
        )

    def getTotalCostCart(self, cart):
        ids = list(cart.keys())
        amounts = list(cart.values())

        for i in range(len(ids)):
            assert type(amounts[i]) == int
            assert amounts[i] > 0

        return self.contract.functions.getTotalCostCart(ids, amounts).call()

    def buyProducts(self, products, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        
        for amount in products.values():
            assert type(amount) == int
            assert amount > 0
        
        total_price = self.getTotalCostCart(products)
        balance = self.getLocalBalance(tx_dict["from"])

        if total_price > balance:
            self.deposit({
                "from": tx_dict["from"],
                "value": total_price - balance 
            })

        private_key = self.get_private_key(tx_dict["from"])

        self.token.increaseAllowance(self.contract_address, total_price, tx_dict)
        self.BuildandSignTX(
            tx_dict["from"], 
            "buyProducts", 
            private_key,
            self.function_structure["buyProducts"], 
            tx_dict, 
            list(products.keys()), 
            list(products.values())
        )

        return total_price