from web3 import Web3, HTTPProvider

from utils import dex_contract, token_contract


def getRemoteBalance(web3, address):
    return web3.eth.get_balance(address)


web3 = Web3(HTTPProvider("http://127.0.0.1:8545"))
print("Connected? ",web3.isConnected())



# dex = web3.eth.contract(address = dex_contract["address"], abi=dex_contract["abi"])
token = web3.eth.contract(address = token_contract["address"], abi=token_contract["abi"])


total_accounts = web3.eth.accounts + [dex_contract["address"]]
for account in total_accounts:
    remote_balance = getRemoteBalance(web3,account)
    local_balance = token.functions.balanceOf(account).call()

    if account == total_accounts[-1]:    
        print(f"Dex contract -> {remote_balance} [{local_balance} tokens]")

    else:
        print(f"{account} -> {remote_balance} [{local_balance} tokens]")
    print()
        



