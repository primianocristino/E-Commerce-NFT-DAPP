//import detectEthereumProvider from '@metamask/detect-provider'

/*
To install web3.js
    Option 1:
        npm i @alch/alchemy-web3
    Option2:
        <script src="https://cdn.jsdelivr.net/npm/@alch/alchemy-web3@latest/dist/alchemyWeb3.min.js"></script>
*/

class MetaMaskWrapper{

    constructor(){        
        // Using WebSockets
        this.web3 = AlchemyWeb3.createAlchemyWeb3("http://127.0.0.1:8545",);
        this.is_wallet_connected = false
        this.account = null
        this.contract = null
        this.contract_address = null
        this.token = null
        this.token_address = null

        this.token_nft = null
        this.token_nft_address = null
    }

    static to_wei(amount, decimals){


        try{

            if (!decimals)
                decimals = 18;

            amount = BigInt(parseInt(amount * parseFloat(10**decimals)))


            /*
             amount = 5000000001000000000 == 5
                      5000000010000000000
            */
        }
        catch{
            console.log("towei error")
            amount = 0
        }
        return amount 
    }
    async retrieveAccountInfo(){
        if(window.ethereum){
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts',
                })
            this.is_wallet_connected = true;
            this.account = accounts[0];
            return this.account;
        }
        else
            throw new Error("No wallet present"); 
        
    }

    setupContract(abi, address){
        this.contract = new this.web3.eth.Contract(abi, address);
        this.contract_address = address;
    }

    setupToken(abi, address){
        this.token = new this.web3.eth.Contract(abi, address);
        this.token_address = address
    }

    setupTokenNft(abi, address){
        this.token_nft = new this.web3.eth.Contract(abi, address);
        this.token_nft_address = address
    }

    /******************Contracts function*****************************/

    
    async totalSupply(tx_dict){
        return this.token.methods.totalSupply().call(tx_dict)
    }

    async currentSupply(tx_dict){
        return this.token.methods.balanceOf(this.contract_address).call()
    }

    /*
    async getRemoteBalance(account){
        //return self.web3.alchemy.getTokenBalances(account, [self.contract_address])
        return window.web3.eth.getBalance(account)
    }
    */

    async balanceOf(tx_dict){
        return this.contract.methods.balanceOf(tx_dict["from"]).call(tx_dict)
    }

    async getURI(product_id, tx_dict){
        return this.contract.methods.getURI(product_id).call(tx_dict)
    }

    /*
    async getProduct(product_id, tx_dict){
        return this.contract.methods.getProduct(product_id).call(tx_dict)
    }
    */


    async increaseSupply(amount, tx_dict){
        const decimals = parseInt(await this.token.methods.decimals().call(tx_dict))

        return this.contract.methods.increaseSupply(MetaMaskWrapper.to_wei(amount, decimals)).send(tx_dict)
    }

    async decreaseSupply(amount, tx_dict){
        const decimals = parseInt(await this.token.methods.decimals().call(tx_dict))

        return this.contract.methods.decreaseSupply(MetaMaskWrapper.to_wei(amount, decimals)).send(tx_dict)
    }

    async addProduct(id, price, stock, discount, is_nft, metadata, tx_dict){

        price = MetaMaskWrapper.to_wei(price)
        console.log("price "+price)
        stock = parseInt(stock)
        

        console.log("PRE ADD PRODUCT")
        console.log("id: ", id, typeof id)
        console.log("price: ", price, typeof price)
        console.log("stock: ", stock, typeof stock)
        console.log("discount: ", discount, typeof discount)
        console.log("is_nft: ", is_nft, typeof is_nft)
        
        

        metadata = CryptoJS.MD5(encodeURI(metadata)).toString()

        console.log("MD5(UTF8(metadata)): ", metadata)

        if(is_nft == true)
            return this.contract.methods.addProduct(id, price, stock, discount, metadata).send(tx_dict)
        else
            return this.contract.methods.addProduct(id, price, stock, discount).send(tx_dict)
    }

    async editProduct(id, price, stock, discount, is_nft, metadata, tx_dict){

        price = MetaMaskWrapper.to_wei(price)
        stock = parseInt(stock)

        console.log("metadata is: ", metadata)
        if(is_nft == true && metadata != "" && metadata != null){
            metadata = CryptoJS.MD5(metadata).toString()
            console.log(metadata)
            return this.contract.methods.editProduct(id, price, stock, discount, metadata).send(tx_dict)
        }
            
        else
            return this.contract.methods.editProduct(id, price, stock, discount).send(tx_dict)

    }

    async deleteProduct(id, tx_dict){
        return this.contract.methods.deleteProduct(id).send(tx_dict)
    }

    async isDexApproved(tx_dict){
        return this.token_nft.methods.isApprovedForAll(tx_dict["from"], this.contract_address).call(tx_dict)
    }

    async deposit(tx_dict){

        if(typeof tx_dict["value"] != "bigint")
            tx_dict["value"] = MetaMaskWrapper.to_wei(tx_dict["value"])
        
        tx_dict["value"] = parseInt(tx_dict["value"])
        return this.contract.methods.deposit().send(tx_dict)
    }

    async withdraw(amount, tx_dict){
        await this.token.methods.minimalIncreaseAllowance(this.contract_address, MetaMaskWrapper.to_wei(amount)).send(tx_dict)
        return this.contract.methods.withdraw(MetaMaskWrapper.to_wei(amount)).send(tx_dict)
    }

    async buyProducts(ids, amounts, tx_dict){

        //return this.contract.methods.getTotalCostCart(ids, amounts).call(tx_dict)
        const total_amount = BigInt(await this.contract.methods.getTotalCostCart(ids, amounts).call(tx_dict))
        //var balance = BigInt(await this.contract.methods.balanceOf(tx_dict["from"]).call(tx_dict))
        var balance = BigInt(await this.balanceOf(tx_dict))

        const valuediff = BigInt(total_amount - balance) //-BigInt(2*10**9) 400000000000000001

        console.log("costo carrello: ", total_amount)
        console.log("saldo conto: ", balance)
        console.log("differenza da pagare: ", valuediff)

        if(total_amount > balance){
            $("#flashbox").attr("class", "alert alert-warning")
            $("#flashbox").text("You need to deposit enough token.")
            window.scrollTo(0, 0)
            await this.deposit({
                from: tx_dict["from"],
                value: valuediff
            })
        }

        balance = BigInt(await this.contract.methods.balanceOf(tx_dict["from"]).call(tx_dict))
        console.log("new balance: "+balance)
        
        //console.log("contract address: "+this.contract_address)
        //console.log(typeof this.contract_address)

        //console.log(typeof this.token.methods)
        //console.log(this.token.methods)
        //total_amount= total_amount - allowance()
        await this.token.methods.minimalIncreaseAllowance(this.contract_address, total_amount).send(tx_dict)
        
        return this.contract.methods.buyProducts(ids, amounts).send(tx_dict)
    }

    conditionTerms(status, tx_dict){
        return this.token_nft.methods.setApprovalForAll(this.contract_address, status).send(tx_dict)
    }

}

var walletWrapper = new MetaMaskWrapper();

/*
class JunkWrapper{
    static provider = null;
    static wallet_set = false;
    constructor(){}

    async checkWallet(){
        if(MetaMaskWrapper.wallet_set == false){
            MetaMaskWrapper.provider = await detectEthereumProvider();
            startApp(MetaMaskWrapper.provider);
            MetaMaskWrapper.wallet_set = true;
        }
    }

    async getProvider(){
        if(MetaMaskWrapper.wallet_set == false){
            await MetaMaskWrapper.checkWallet();
            if (MetaMaskWrapper.wallet_set == false)
                throw new Error("MetamaskWallet is not detected")
        }

        if(MetamaskWrapper.provider == null || MetaMaskWrapper.provider.isConnected() == false)
            throw new Error('MetamaskWallet is not connected')

        return MetaMaskWrapper.provider
    }
}
*/
//var walletWrapper = new MetaMaskWrapper()

