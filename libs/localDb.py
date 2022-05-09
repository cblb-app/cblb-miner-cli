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
from actions import checkinController

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def genStateJson():
    open(os.getenv('STATE_JSON'), 'w') 
    log.logOneLine('Init state json file')

# update leader and miner wallet info
# MATIC balance
# CBLB balance
# checkin waiting time
def updateAll():
    minWaitSecond = float(os.getenv('CHECKIN_ONE_DAY_DURATION'))
    isNeedFund = False

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
            gap =  checkinController.getCheckinGap(w3, wallets.leader)

            if float(gap) > float(os.getenv('CHECKIN_ONE_DAY_DURATION')):
                minWaitSecond = 0
            else:
                if minWaitSecond > float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap):
                    minWaitSecond = float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap)

            
            if float(matic) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
                isNeedFund = True

            # insert data
            db.insert({
                'address': str(wallets.leader.address),
                'matic': str(matic),
                'cblb': str(cblb),
                'gap': str(gap)
            })
            log.logOneLine('Index local db: leader index address ' + 
                wallets.leader.address + 
                ', MATIC balance ' + 
                str(matic) + 
                ', CBLB balance ' + 
                str(cblb) + 
                ', checkin gap ' + 
                str(gap))

            for miner in wallets.miners:
                matic = balanceController.getMaticBalance(w3, miner)
                cblb = balanceController.getCblbBalance(w3, miner)
                gap =  checkinController.getCheckinGap(w3, miner)

                if float(gap) > float(os.getenv('CHECKIN_ONE_DAY_DURATION')):
                    minWaitSecond = 0
                else:
                    if minWaitSecond > float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap):
                        minWaitSecond = float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap)

                if float(matic) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
                    isNeedFund = True

                db.insert({
                    'address': miner.address, 
                    'matic': str(matic),
                    'cblb': str(cblb),
                    'gap': str(gap)
                })
                log.logOneLine('Index local db: miner address ' + 
                    miner.address + 
                    ', MATIC balance ' + 
                    str(matic) + 
                    ', CBLB balance ' + 
                    str(cblb)+ 
                    ', checkin gap ' + 
                    str(gap))
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
            gap =  checkinController.getCheckinGap(w3, wallets.leader)

            if float(gap) > float(os.getenv('CHECKIN_ONE_DAY_DURATION')):
                minWaitSecond = 0
            else:
                if minWaitSecond > float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap):
                    minWaitSecond = float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap)

            if float(matic) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
                isNeedFund = True

            updateAddressBalance(wallets.leader.address, str(matic), str(cblb), str(gap))
            
            log.logOneLine('Update local db: leader address ' + 
                wallets.leader.address + 
                ', MATIC balance ' + 
                str(matic) + 
                ', CBLB balance ' + 
                str(cblb) + 
                ', checkin gap ' + 
                str(gap))

            for miner in wallets.miners:
                matic = balanceController.getMaticBalance(w3, miner)
                cblb = balanceController.getCblbBalance(w3, miner)
                gap =  checkinController.getCheckinGap(w3, miner)

                if float(gap) > float(os.getenv('CHECKIN_ONE_DAY_DURATION')):
                    minWaitSecond = 0
                else:
                    if minWaitSecond > float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap):
                        minWaitSecond = float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(gap)

                if float(matic) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
                    isNeedFund = True

                updateAddressBalance(miner.address, str(matic), str(cblb), str(gap))
               
                log.logOneLine('Update local db: miner address ' + 
                    miner.address + 
                    ', MATIC balance ' + 
                    str(matic) + 
                    ', CBLB balance ' + 
                    str(cblb) + 
                    ', checkin gap ' + 
                    str(gap))
    
    return {
        'minWaitSecond': minWaitSecond,
        'isNeedFund': isNeedFund
    }

def updateAddressBalance(address, matic, cblb, gap):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    
    if len(itemDictArray) == 0:
        log.logOneLine('[Error]: Can NOT found target address in localDb, please delete state.json file rerun cblb-miner')

    assert len(itemDictArray) > 0

    db.update({
        'address': address, 
        'matic': str(matic),
        'cblb': str(cblb),
        'gap': str(gap)
    }, wallet.address == address)

def updateAddressMaticBalance(address, matic):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    db.update({
        'address': address, 
        'matic': str(matic),
        'cblb': itemObj.cblb,
        'gap': itemObj.gap
    }, wallet.address == address)

def updateAddressCblbBalance(address, cblb):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    db.update({
        'address': address, 
        'matic': itemObj.matic,
        'cblb': str(cblb),
        'gap': itemObj.gap
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

def getCheckinGap(address):
    db = TinyDB(os.getenv('STATE_JSON'))
    wallet = Query()
    itemDictArray = db.search(wallet.address == address)
    itemObj = DefaultMunch.fromDict(itemDictArray[0])
    return itemObj.gap
