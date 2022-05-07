from eth_account import Account
import secrets
import json
import os
from munch import DefaultMunch
from dotenv import load_dotenv

# local import 
import libs.log as log

load_dotenv()

def genWalletAndSave():
    minerNumber = int(os.getenv('MINER_NUMBER'))

    leaderWallet = genOneWallet()
    minerWallet = []
    for i in range(minerNumber):
        minerWallet.append(genOneWallet())

    walletDict = {
        'leader': leaderWallet,
        'miners': minerWallet
    }

    walletObj = DefaultMunch.fromDict(walletDict)
    log.logOneLine('Gen wallets, leader address is ' + walletObj.leader.address)
    with open(os.getenv('WALLET_JSON'), 'w') as f:
        json.dump(walletDict, f)
        log.logOneLine('Init wallet json file')

def genOneWallet():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    address = Account.from_key(private_key).address
    walletObj = {
        'pkey': private_key,
        'address': address
    }
    return walletObj
