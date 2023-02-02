from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from solcx import compile_files, compile_standard, install_solc, set_solc_version
from utils import StorageHandler
from utils import defaultgas, networkID, contract_debug, debug_file
from utils import contract_compiler_version, default_gas_price
from utils import admin_info
import json


class ContractWrapper:
    def __init__(self,name, web3host, web3type = "HTTP", defaultgas = defaultgas, network_ID = networkID["value"], debug = contract_debug, debug_file = debug_file):
        
        if web3type == "HTTP":
            Web3instance=Web3(HTTPProvider(web3host))
        if network_ID==4:
            Web3instance.middleware_stack.inject(geth_poa_middleware, layer=0)

        self.debug = debug
        
        if self.debug:
            self.debug_file = debug_file
        else:
            self.debug_file = {}

        self.name = name
        self.contract_address = None
        self.contract_abi = None
        self.contract = None
        self.contract_compiled = False

        self.gas=defaultgas
        self.chainId=network_ID
        self.Web3=Web3instance

        # self.debug_accounts_index = {self.Web3.eth.accounts[i]:i for i in range(len(self.Web3.eth.accounts))}
    def get_private_key(self, address):
        assert self.debug
        assert address in self.debug_file.keys()
  
        return self.debug_file[address]

    def compile_contract(self, *args, compiler_version=contract_compiler_version, **kwargs):
        # compile all contract files
        # install_solc(compiler_version)

        set_solc_version(compiler_version)

        solidity_sources = [StorageHandler.getContract(arg, super_contract=self.name) for arg in args]

        solidity_sources.append(StorageHandler.getContract(self.name))
        contracts = compile_files(solidity_sources)

        self.contract_compiled = True

        contract_interface = contracts.pop(StorageHandler.getContract(self.name)+":"+self.name)

        if "compiled_files" in kwargs and type(kwargs["compiled_files"]) == list:
            interfaces = {}

            for c_file in kwargs["compiled_files"]:
                try:
                    interfaces[c_file] = contracts.pop(StorageHandler.getContract(c_file, super_contract=self.name)+":"+c_file)
                except:
                    print(f"[Error] {c_file} contract not found")

            interfaces[self.name] = contract_interface
            
            return interfaces
        else:
            return contract_interface

    def deploy_contract(self, contract_interface, *args):

        pre_deployed_contract = self.Web3.eth.contract(
        bytecode = contract_interface["bin"],
        abi = contract_interface["abi"]
        )

        tx_receipt = self.BuildandSignTX(
            admin_info["address"],
            None, 
            admin_info["private_key"],
            None,
            {},
            *args, 
            call_constructor = True, 
            pre_deployed_contract = pre_deployed_contract 
        )

        self.contract_address = tx_receipt["contractAddress"]
        self.contract_abi = contract_interface["abi"]

        self.contract = self.Web3.eth.contract(address=self.contract_address, abi=self.contract_abi )

    def toWei(self, eth, scale = "ether"):
        return self.Web3.toWei(str(eth), scale)

    def fromWei(self, wei, scale = "ether"):
        return self.Web3.fromWei(str(wei), scale)

    def getRemoteBalance(self, address):
        return self.Web3.eth.get_balance(address)

    def SendFunctionTransaction(self,privatekey,txn_dict):
        

        signed_txn = self.Web3.eth.account.signTransaction(txn_dict, privatekey)

        result = self.Web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_receipt = self.Web3.eth.waitForTransactionReceipt(result)

        return tx_receipt 

    def getFunction(self, functionName, function_structure):
            FUNCS = self.contract.find_functions_by_name(functionName)
            
            if len(FUNCS) <= 0:
                return None
            else:
                index = -1
                for i in range(len(FUNCS)):
                    if function_structure in str(FUNCS[i]):
                        index = i
                        break
                
                assert index >= 0
            return FUNCS[index]

    def BuildContractTX(self,nonce,functionName, function_structure, tx_dict, *args, **kwargs):

        if "call_constructor" in kwargs.keys() and kwargs["call_constructor"]:
            # self.debug == True and print("CONSTRUCTOR")
            FUNC = kwargs["pre_deployed_contract"].constructor
        else:
            # self.debug == True and print("NO CONSTRUCTOR")
            # FUNC=self.contract.get_function_by_name(functionName)
            # FUNCS = self.contract.find_functions_by_name(functionName)
            
            FUNC = self.getFunction(functionName, function_structure)
            assert FUNC != None

        if "gasprice" not in kwargs.keys() or kwargs["gasprice"] is None:
            # print("[INFO] Default gasprice is set")
            gasprice = self.Web3.toWei(str(default_gas_price), 'gwei')
        else:
            print("[INFO] Custom gas price is set")
            gasprice=kwargs["gasprice"]  
            
        local_tx_dict = {
            'chainId':  self.chainId,
            # 'gas': gasEstimated,
            'gasPrice': gasprice,
            'nonce': nonce,
        }

        tx_dict = {**local_tx_dict, **tx_dict}

        # tx_dict["gas"] = gasEstimated

        # print("args: ",args)

        print("GAS ESTIMATED: ", FUNC(*args).estimate_gas(tx_dict))
        builtTX=FUNC(*args).buildTransaction(tx_dict)
        
        return builtTX
 

    def callFunctionTransaction(self,functionName,*args):
        try:
            FUNC=self.contract.get_function_by_name(functionName)
            
            return FUNC(*args).call() 
                        
        except Exception as error:
            print(error)
       
    def BuildandSignTX(self,address,functionName,private_key, function_structure, tx_dict, *args, **kwargs):
        nonce= self.Web3.eth.getTransactionCount(address)
        
        # print("Pre build")
        tx=self.BuildContractTX(nonce, functionName, function_structure, tx_dict, *args, **kwargs)
        # print("POST build")
        return self.SendFunctionTransaction(private_key,tx)