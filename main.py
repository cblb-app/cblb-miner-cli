from web3 import Web3
from dotenv import load_dotenv
import os
import json
import time
from munch import DefaultMunch
from decimal import Decimal
# for Polygon add middleware
from web3.middleware import geth_poa_middleware

# module
import libs.wallet as wallet
import libs.log as log
import actions.checkinController as checkinController
import actions.balanceController as balanceController
import libs.localDb as localDb

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
wallets = {}
log.logOneLine('-------CBLB MINER-------')
log.logOneLine('Official Website: https://cblb.app')
log.logOneLine('CBLB token issued on Polygon blockchain')
log.logOneLine('CBLB token address: ' + os.getenv('CBLB_TOKEN_CONTRACT_ADDRESS'))
log.logOneLine('Cblb Check-in contract address: ' + os.getenv('CBLB_CHECKIN_CONTRACT_ADDRESS'))
log.logOneLine('')

log.logOneLine('Miner self checking...')
# remove older log files
log.removeExpiredLogFiles()

# check wallet.json is exist or NOT, if NOT, gen one
log.logOneLine('Checking wallet.json file')
isWalletExist = os.path.exists(os.getenv('WALLET_JSON'))

if not isWalletExist:
    log.logOneLine('   No wallet.json, generate one with ' + os.getenv('MINER_NUMBER') + ' miners')
    wallet.genWalletAndSave()
else:
    log.logOneLine('   Found wallet.json')

# load wallet
with open(os.getenv('WALLET_JSON'), 'r') as f:
    walletDict = json.load(f)
    wallets = DefaultMunch.fromDict(walletDict)
    
    if int(os.getenv('MINER_NUMBER')) == len(wallets.miners):
        log.logOneLine('   Wallet json miner number equals .env file record. Total miners ' + str(len(wallets.miners)))
        log.logOneLine('   Leader wallet address:'+ wallets.leader.address)
    else:
        log.logOneLine('[ERROR]: Wallet json miner number is ' + str(len(wallets.miners)) +' NOT equals .env file record ' + os.getenv('MINER_NUMBER')+'. Please backup current wallet.json file to safe place, and delete it from cblb-py-miner folder. cblb-py-miner will regenerate one for you.')
        exit()


# can connect blockchain
log.logOneLine('Checking rpc connection...')
if not w3.isConnected():
    log.logOneLine('[ERROR]Can NOT connect chain with rpc '+ os.getenv("RPC_URL") + ', please check your internet connection and rerun cblb-py-miner')
    log.logOneLine('Exiting')
    exit()
else:
    log.logOneLine('   Rpc connection is good')


log.logOneLine('Start checkin mining loop')

while True:
    try:
        # remove older log files
        log.removeExpiredLogFiles()

        # update db
        stateDict = localDb.updateAll()
        stateObj = DefaultMunch.fromDict(stateDict)
        
        # balancer wallets
        balanceController.balanceLeaderAndMinerMatic(w3, wallets.leader, wallets.miners)

        # checkin all
        checkinController.checkinAll(w3, wallets.leader, wallets.miners)

        # collect all
        balanceController.collectLeaderMinerCblb(w3, wallets.leader, wallets.miners)

        # collect mini matic
        balanceController.collectMiniMaticToLeaderWallet(w3, wallets.leader, wallets.miners)

        if bool(stateObj.isNeedFund):
            balanceController.waitFundLoop(w3, wallets.leader)

        log.logOneLine('Finish one checkin-mining loop for leader wallet and ' + os.getenv('MINER_NUMBER') + ' miners.')
        log.logOneLine('Waiting ' + str(stateObj.minWaitSecond) + ' seconds for next checkin-mining loop...')
        time.sleep(int(stateObj.minWaitSecond))
    except:
        log.logOneLine('Cblb miner dead, restarting')