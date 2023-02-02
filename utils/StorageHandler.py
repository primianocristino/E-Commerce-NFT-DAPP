import ast, os, pickle, json

class StorageHandler():

    @staticmethod
    def __load_pickle(file_name: str, folder: str):
        file = os.path.join(folder, file_name)
        if not os.path.exists(file):
            return None
        with open(file, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def __save_pickle(obj, file_name: str, folder: str):
        file = os.path.join(folder, file_name)

        with open(file, "wb") as f:
            pickle.dump(obj, f)


    @staticmethod
    def __cd_parent(file):
        return os.path.dirname(file)

    @staticmethod
    def __get_project_directory():
        return StorageHandler.__cd_parent(os.path.realpath(__file__))

    @staticmethod
    def __get_root_directory():
        return StorageHandler.__cd_parent(StorageHandler.__get_project_directory())


    @staticmethod
    def get_admin_dir():
        return os.path.join(StorageHandler.__get_project_directory(), "static", "images", "admin_profile")

    @staticmethod
    def get_customer_dir():
        return os.path.join(StorageHandler.__get_project_directory(), "static", "images", "customer_profile")


    @staticmethod
    def create_directories():
        if not os.path.exists(StorageHandler.get_admin_dir()):
            os.mkdir(StorageHandler.get_admin_dir())

        if not os.path.exists(StorageHandler.get_customer_dir()):
            os.mkdir(StorageHandler.get_customer_dir())


    def get_config_file_path(filename):
        return os.path.join(StorageHandler.__get_root_directory(), "utils", filename)

    @staticmethod
    def save_json(json_name, data):
        file_path = StorageHandler.get_config_file_path(json_name)

        data_json = json.loads(json.dumps(data))
        with open(file_path, "w", encoding="utf-8") as f: 
            json.dump(data_json, f, ensure_ascii=False, indent=4)
        
    @staticmethod
    def load_json(json_name):
        file_path = StorageHandler.get_config_file_path(json_name)
        try:
            with open(file_path, "r") as f:

                data_json = json.load(f)
        except:
            data_json = None
            
        return data_json

    @staticmethod
    def getContractDir():
        return os.path.join(StorageHandler.__get_root_directory(),"contracts")

    @staticmethod
    def getContract(filename: str, super_contract = ""):
        if super_contract == "":
            super_contract = filename
        return os.path.join(StorageHandler.getContractDir(), super_contract, filename + ".sol").replace("\\","/")

    @staticmethod
    def getGenericContractExtraFile(filename: str):
        return os.path.join(StorageHandler.getContractDir(), filename).replace("\\","/")

    @staticmethod
    def save_contract(contract, filename, super_contract = ""):
        if super_contract == "":
            super_contract = filename

        file_path = os.path.join(StorageHandler.getContractDir(),super_contract, filename + ".json")
        with open(file_path,"w",encoding="utf-8") as f:
            f.write(str(contract))
        
        if super_contract == filename:
            print("Contract saved: ", filename)
        else:
            print("Contract saved: ", filename, " of ",super_contract)

    @staticmethod
    def load_contract(filename, super_contract = ""):
        if super_contract == "":
            super_contract = filename

        file_path = os.path.join(StorageHandler.getContractDir(), super_contract, filename + ".json")
        if os.path.exists(file_path):    
            with open(file_path,"r",encoding="utf-8") as f:
                data = f.readline()

            # print(type(ast.literal_eval(data)))
            return ast.literal_eval(data)

        print("[ERROR] No contract found")
        return {}
            