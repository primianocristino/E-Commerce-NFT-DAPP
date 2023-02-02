from utils import StorageHandler


def getServerData():
    try:
        json_data = StorageHandler.load_json("server_info.json")
        json_data_keys = list(json_data.keys())

        must_keys = ["protocol","host","port","api"]
        for key in must_keys:
            if key not in json_data_keys:
                raise Exception("[Warning] "+key+" not found in server_info.json")
            elif key == "port":
                try:
                    json_data[key] = int(json_data[key])
                except:
                    raise Exception("[Warning] port must be a number")
        
        return json_data
    except Exception as e:
        print(e)
        print("[Warning] using built-in parameters")
        print()
        json_data = {
            "protocol": "http",
            "host": "127.0.0.1",
            "port": 5000,
            "api": "nftMetadata" 
        }
        return json_data

def getAdminInfo():
    json_data = StorageHandler.load_json("admin_info.json")
    json_keys = list(json_data.keys())

    if "address" not in json_keys or "private_key" not in json_keys:
        raise Exception("Invalid address info")

    return json_data

def getTestAccounts():
    try:
        return StorageHandler.load_json("test_accounts.json")
    except Exception as e:
        print(e)
        return {}

basedir = {"value": None}
image_complete_path = {"value": None}
ip_dict = {"value": "127.0.0.1"}

defaultgas = 50000
default_gas_price = 20 # in gwei

contract_compiler_version = "0.8.0"
contract_debug = False
debug_file = getTestAccounts()



web3_protocol = "http"
web3_domain = "127.0.0.1"
web3_port = "8545"

web3_uri = {
    "value": web3_protocol + "://" + web3_domain + ":" + web3_port
}
networkID = {"value": 1337}

# server_protocol, server_host, server_port, server_api = getServerData()
server_data = getServerData()
admin_info = getAdminInfo()





# dex_contract = {"instance": None}
dex_contract = StorageHandler.load_contract("DEX")
assert dex_contract != {}

token_contract = StorageHandler.load_contract("ERC20Token", super_contract="DEX")
assert token_contract != {}

token_nft_contract = StorageHandler.load_contract("ERC721Token", super_contract="DEX")
assert token_nft_contract != {}

dex_instance = {"value": None}
tmp_nft = {}
# ----------------------

# dex_json = StorageHandler.load_contract("DEX")
# dex_contract = DEX.at(address=dex_json["address"])
def get_IP():
    return ip_dict["value"]