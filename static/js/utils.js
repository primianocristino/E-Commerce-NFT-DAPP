String.prototype.replaceAt = function(index, replacement) {
    return this.substring(0, index) + replacement + this.substring(index + replacement.length);
}

function adjustBalance(balance) {
    real_balance = ""
    int_part = (BigInt("" + balance) / BigInt("" + 10 ** 18)).toString()

    if (int_part == "0") {
      real_balance = "0." + "0".repeat(19 - balance.length - 1) + balance
    }
    else {
      decimal_part = balance.substring(int_part.length, balance.length)
      if (decimal_part == "")
        decimal_part = "0"
      real_balance = "" + int_part + "." + decimal_part
    }
    /*
        5000000000000000 = 0.005 ETH
    50000000000000000 = 0.05  ETH
    500000000000000000 = 0.5   ETH
    1000000000000000000 = 1.0   ETH
        5000000000000000
    */

    return real_balance
}

async function moneyWorkFlow(type) {
    console.log("My TYPE IS: ", type)
    console.log("Before get contarct")
    walletWrapper.setupContract(contract_abi, contract_address)
    walletWrapper.setupToken(token_abi, token_address)
    console.log("after get contract")
    account = await walletWrapper.retrieveAccountInfo()
    if (type == "Deposit")
        await walletWrapper.deposit(
            {
                from: account,
                value: $("#amount").val()
            })
    else if (type == "Withdraw")
        await walletWrapper.withdraw(
            $("#amount").val(),
            {
                from: account
            })
    else if (type == "IncreaseSupply") {

        await walletWrapper.increaseSupply(
            $("#amount_supply").val(),
            {
                from: account
                //gas: 6721975
            })
    }
    else if (type == "DecreaseSupply") {
        await walletWrapper.decreaseSupply(
            $("#amount_supply").val(),
            {
                from: account
                //gas: 6721975
            })
    }

    //console.log("HERE")
    if (type == "Deposit" || type == "Withdraw" || type.includes("BalanceOf")) {
        //console.log("ARA ARA")
        var balance = await walletWrapper.balanceOf(
            {
                from: account
            })

        $("#balance").text("Balance: ETH " + adjustBalance(balance));

    }
    else if (type.includes("Supply")) {
        var balance = await walletWrapper.currentSupply(
            {
                from: account
            })

        var supply = await walletWrapper.totalSupply(
            {
                from: account
            })

        $("#currentSupply").text("Current: ETH " + adjustBalance(balance));
        $("#supply").text("Total supply: ETH " + adjustBalance(supply));

    }

    removeTrailing()
    console.log(type + " done")
}

function deposit() {
    moneyWorkFlow("Deposit")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}


function withdraw() {
    moneyWorkFlow("Withdraw")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function balanceOf() {
    moneyWorkFlow("LocalBalanceOf")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function remoteBalanceOf() {
    moneyWorkFlow("RemoteBalanceOf")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function increaseSupply() {
    moneyWorkFlow("IncreaseSupply")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function decreaseSupply() {
    moneyWorkFlow("DecreaseSupply")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function totalSupply() {
    moneyWorkFlow("TotalSupply")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

function currentSupply() {
    moneyWorkFlow("CurrentSupply")
        .catch(error => {
            message = getMetamaskError(error.message)

            $("#flashbox").attr("class", "alert alert-danger")
            $("#flashbox").text(message)
            window.scrollTo(0, 0)
        })
}

async function conditionTerms(){
    console.log("Before get contarct")
    walletWrapper.setupContract(contract_abi, contract_address)
    walletWrapper.setupTokenNft(token_nft_abi, token_nft_address)
    console.log("after get contract")
    account = await walletWrapper.retrieveAccountInfo()
    await walletWrapper.conditionTerms({
        from: account
    })
    return account
}

function getMetamaskError(error){
    error = error.replace("[ethjs-query] while formatting outputs from RPC ","")
    message = ""
    try{

        error = error.replaceAll('\n','')
        error = error.replaceAll('"',"'")
        error = error.replaceAt(0,'"')
        error = error.replaceAt(error.length -1,'"')

        error = error.split("VM Exception while processing transaction: revert ")[1]
        message = error.split("','")[0]

    }
    catch(err){
        console.log(err)
        message = "A generic error is occured"
    }

    return message
}
