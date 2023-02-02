from .ContractWrapper import ContractWrapper
from utils import web3_uri

class ERC721Token(ContractWrapper):
    def __init__(self, address = None, abi = None, debug = False):
        super(ERC721Token, self).__init__("ERC721Token", web3_uri["value"], debug = debug)

        self.contract_address = address
        self.contract_abi = abi

        self.contract = self.Web3.eth.contract(address=self.contract_address, abi=self.contract_abi)

        self.function_structure = {}

        funcs_std = ["setApprovalForAll", "setServerData"]
        for fun in funcs_std:
            FUN_str = str(self.contract.get_function_by_name(fun))
            self.function_structure[fun] = "("+FUN_str.split("(")[1].split(")")[0]+")"


    def toHex(self, data):
        return self.Web3.toHex(data)

    def getURI(self, product_id):
        return self.contract.functions.getURI(product_id).call()

    def getMetadataHash(self,product_id):
        return self.contract.functions.getMetadataHash(product_id).call()

    def isApprovedForAll(self, owner, operator):
        return self.contract.functions.isApprovedForAll(owner, operator).call()

    def setApprovalForAll(self, operator, allowed, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert type(allowed) == bool

        private_key = self.get_private_key(tx_dict["from"])

        self.BuildandSignTX(
            tx_dict["from"], 
            "setApprovalForAll", 
            private_key, 
            self.function_structure["setApprovalForAll"], 
            tx_dict, 
            operator, 
            allowed
        )

    def getServerData(self):
        return self.contract.functions.getServerData().call()

    def setServerData(self, server_protocol, server_host, server_port, server_api, admin_key, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts

        assert type(server_port) == int
        assert server_port >=1025 and server_port <= 655536

        self.BuildandSignTX(
            tx_dict["from"], 
            "setServerData", 
            admin_key, 
            self.function_structure["setServerData"], 
            tx_dict, 
            server_protocol,
            server_host,
            str(server_port),
            server_api
        )
