<h1>E-commerce NFT DAPP</h1>

This project implements a distributed application for an NFT e-commerce, built in Flask, based on smart contract interactions between a remote wallet (e.g. Metamask) and an ethereum blockchain. The DAPP uses Web3.js for the communication with Metamask and the blockchain instance running on Ganache.

<h2>Requirements</h2>
<ul>
  <li>
    Blockchain instance running on whatever platform (Ganache, Infura, Truffle, etc...)
  </li>
  <li>
    Remote wallet browser extension
  </li>
  <li>
    Web3.js library
  </li>
  <li>
  Web3.py for Python debugging tests
  </li>
</ul>

<h2>Installation</h2>
First you need to install all the required libraries with the following command:

```console
pip install -r requirements.txt
```
This project uses Ganache-cli to run the blockchain instance with a specific set of accounts which can be exported by the wallet browser extension (e.g. Metamask).

```shell
ganache-cli --networkId=1337 --db="./instance/blockchain" --gasLimit=20000000 [--account="0x<Account private key>,<Balance in Wei>"]
```


<h2>Run</h2>

The DAPP is associated with admin address in the blockchain. This address is responsible for the deploying of DEX contract. 
You have to add the admin credentials (address and private key) in the file <i><b>admin_info.json</b></i> in the utils directory.
This json must have the following structure:
```file
{
    "address": "<admin address>",
    "private_key": "0x<admin private key>"
}
```

Second you have to compile and deploy the smart contract of the DAPP.

```console
python deployDex.py
```
If Everything goes well, you see something like following:

```shell
Contract saved:  DEX
Contract saved:  ERC20Token  of  DEX
Contract saved:  ERC721Token  of  DEX
```
If you want to run the application you need to execute the following command: 

```console
python app.py -web3-protocol="http" -web3-host="127.0.0.1" -web3-port="8545" -blockchain-networkId="1337"
```
The application will be located at the link http://127.0.0.1:5000


<h2>Optional Test</h2>

If you want to test the DEX contract, you have to add two different acoounts in the file <i><b>test_accounts.json</b></i> in the utils directory.
This json must have the following structure:
```file
{
    "<buyer address>": "0x<buyer private key>",
    "<seller address>": "0x<seller private key>",
}
```
In order to run the test, you have to execute the following command:
```console
python testContract.py
```

<h2>Notes</h2>

<ul>
  <li>
    This project run the web server and the ganache enviroment on the same machine. 
    So if you want to change the server configuration you have to edit the file <i><b>server_info.json</b><i> in the utils directory.
  </li>
  <li>
  In order to run properly the script <i><b>testContract.py</b></i>, the blockchain must contain the same accounts and private keys of those contained in <i><b>test_accounts.json</b> in the utils directory</i> 
  </li>
</ul>
