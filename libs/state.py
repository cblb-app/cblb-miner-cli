import os
import json
import time
from dotenv import load_dotenv
from munch import DefaultMunch
from tinydb import TinyDB, Query
from web3 import Web3
from web3.middleware import geth_poa_middleware

# module
from libs import log
from actions import balanceController

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def genStateJson():
    open(os.getenv('STATE_JSON'), 'w') 
    log.logOneLine('Init state json file')

def updateAll():
    log.logOneLine('-------Update leader and miner balance to local db-------')
    isStateJsonExist = os.path.exists(os.getenv('STATE_JSON'))
    if not isStateJsonExist:
        log.logOneLine('   No state.json, generate one')
        genStateJson()

        # load state
        db = TinyDB(os.getenv('STATE_JSON'))

        # load wallet
        with open(os.getenv('WALLET_JSON'), 'r') as f:
            walletDict = json.load(f)
            wallets = DefaultMunch.fromDict(walletDict)
            matic = balanceController.getMaticBalance(w3, wallets.leader)
            cblb = balanceController.getCblbBalance(w3, wallets.leader)

            # insert data
            db.insert({
                'address': str(wallets.leader.address),
                'matic': str(matic),
                'cblb': str(cblb)
            })
            log.logOneLine('Index local db: leader index address ' + wallets.leader.address + ', MATIC balance ' + str(matic) + ', CBLB balance ' + str(cblb))

            for miner in wallets.miners:
                matic = balanceController.getMaticBalance(w3, miner)
                cblb = balanceController.getCblbBalance(w3, miner)

                db.insert({
                    'address': miner.address, 
                    'matic': str(matic),
                    'cblb': str(cblb)
                })
                log.logOneLine('Index local db: miner address ' + miner.address + ', MATIC balance ' + str(matic) + ', CBLB balance ' + str(cblb))
    else:
        #update
        # load state
        db = TinyDB(os.getenv('STATE_JSON'))

        # load wallet
        with open(os.getenv('WALLET_JSON'), 'r') as f:
            walletDict = json.load(f)
            wallets = DefaultMunch.fromDict(walletDict)
            matic = balanceController.getMaticBalance(w3, wallets.leader)
            cblb = balanceController.getCblbBalance(w3, wallets.leader)

            updateAddressBalance(wallets.leader.address, str(matic), str(cblb))
            
            log.logOneLine('Update local db: leader address ' + wallets.leader.address + ', MATIC balance ' + str(matic) + ', CBLB balance ' + str(cblb))

            for miner in wallets.miners:
                matic = balanceController.getMaticBalance(w3, miner)
                cblb = balanceController.getCblbBalance(w3, miner)

                updateAddressBalance(miner.address, str(matic), str(cblb))
               
                log.logOneLine('Update local db: miner address ' + miner.address + ', MATIC balance ' + str(matic) + ', CBLB balance ' + str(cblb))

def updateAddressBalance(address, matic, cblb):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    db.update({
        'address': address, 
        'matic': str(matic),
        'cblb': str(cblb)
    }, wallet.address == address)

def updateAddressMaticBalance(address, matic):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    db.update({
        'address': address, 
        'matic': str(matic),
        'cblb': itemObj.cblb
    }, wallet.address == address)

def updateAddressCblbBalance(address, cblb):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    db.update({
        'address': address, 
        'matic': itemObj.matic,
        'cblb': str(cblb)
    }, wallet.address == address)


def getAddressMaticBalance(address):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    return itemObj.matic

def getAddressCblbBalance(address):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    return itemObj.cblb
