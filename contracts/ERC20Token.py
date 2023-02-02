from .ContractWrapper import ContractWrapper
from utils import web3_uri


class ERC20Token(ContractWrapper):
    def __init__(self, address, abi, debug = False):
        super(ERC20Token, self).__init__("ERC20Token", web3_uri["value"], debug = debug)

        self.contract_address = address
        self.contract_abi = abi

        self.contract = self.Web3.eth.contract(address=self.contract_address, abi=self.contract_abi)

        self.function_structure = {}

        funcs_std = ["increaseAllowance"]
        for fun in funcs_std:
            FUN_str = str(self.contract.get_function_by_name(fun))
            self.function_structure[fun] = "("+FUN_str.split("(")[1].split(")")[0]+")"

    def increaseAllowance(self, spender, amount, tx_dict):
        assert "from" in tx_dict.keys()
        assert tx_dict["from"] in self.Web3.eth.accounts
        assert amount - int(amount) == 0

        amount = int(amount)
        private_key = None

        private_key = self.get_private_key(tx_dict["from"])

        spender = self.BuildandSignTX(
            tx_dict["from"], 
            "increaseAllowance", 
            private_key, 
            self.function_structure["increaseAllowance"], 
            tx_dict, 
            spender, 
            amount
        )