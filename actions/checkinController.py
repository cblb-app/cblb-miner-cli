import os
import json
import time
from dotenv import load_dotenv
from munch import DefaultMunch
from web3 import Web3
# modules
from libs import log
from libs import localDb

load_dotenv()

chainId = int(os.getenv("CHAIN_ID"))

def checkinAll(w3, leaderWalletObj, minersWalletArray):
    log.logOneLine('-------Checkin actions for leader and miners-------')
    checkin(w3, leaderWalletObj)
    for minerWalletObj in minersWalletArray:
        checkin(w3, minerWalletObj)

def checkin(w3, walletObj):
    balanceMatic = localDb.getAddressMaticBalance(walletObj.address)

    if not float(balanceMatic) > float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
        log.logOneLine('Wallet '+ walletObj.address + ' MATIC balance is '+ balanceMatic +' unsuffi for checkin, make sure there at least '+ os.getenv('CHECKIN_MATIC_BALANCE_MIN')+ ' MATIC')
    else:
        # load abi
        abiCblbCheckinContract = {}
        with open('abi.json', 'r') as f:
            abiDict = json.load(f)
            abiObj = DefaultMunch.fromDict(abiDict)
            abiCblbCheckinContract = abiObj.cblbCheckinContractAbi

        # interact with contract
        cblbCheckinContractInstance = w3.eth.contract(address=os.getenv('CBLB_CHECKIN_CONTRACT_ADDRESS'), abi=abiCblbCheckinContract)
        # checkinGap = cblbCheckinContractInstance.functions.getCheckinGap().call({'from': walletObj.address})
        checkinGap = localDb.getCheckinGap(walletObj.address)

        # checkin gap is more than 1 day?
        if not float(checkinGap) > float(os.getenv('CHECKIN_ONE_DAY_DURATION')):
            log.logOneLine('Wallet ' + walletObj.address +' last checkin within one day, please wait '+ str((float(os.getenv('CHECKIN_ONE_DAY_DURATION')) - float(checkinGap)) / 60) + ' mins')
        else:
            log.logOneLine('Execute checkin action for wallet address ' + walletObj.address)
            nonce = w3.eth.get_transaction_count(walletObj.address)
            # checkin
            storeTxn = cblbCheckinContractInstance.functions.checkin().buildTransaction({
                'nonce': nonce,
                'from': walletObj.address,
                'value': w3.toWei(os.getenv('CHECKIN_FEE'), 'wei'),
                'chainId': chainId,
                'maxFeePerGas': w3.toWei(os.getenv('MAX_FEE_PER_GAS'), 'gwei')
            })

            signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=walletObj.pkey)
            sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
            log.logOneLine('   Send checkin transaction...')
            txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
            log.logOneLine('   Transaction receipt received')
            log.logOneLine('   Finish address ' + walletObj.address + ' checkin and acquire CBLB')


def getCheckinGap(w3, walletObj):
    # load abi
    abiCblbCheckinContract = {}
    with open('abi.json', 'r') as f:
        abiDict = json.load(f)
        abiObj = DefaultMunch.fromDict(abiDict)
        abiCblbCheckinContract = abiObj.cblbCheckinContractAbi

    # interact with contract
    cblbCheckinContractInstance = w3.eth.contract(address=os.getenv('CBLB_CHECKIN_CONTRACT_ADDRESS'), abi=abiCblbCheckinContract)
    checkinGap = cblbCheckinContractInstance.functions.getCheckinGap().call({'from': walletObj.address})
    return checkinGap

def getCurrCheckinCblbAmount(w3, walletObj):
    # load abi
    abiCblbCheckinContract = {}
    with open('abi.json', 'r') as f:
        abiDict = json.load(f)
        abiObj = DefaultMunch.fromDict(abiDict)
        abiCblbCheckinContract = abiObj.cblbCheckinContractAbi
        log.logOneLine('Loaded checkin contract abi')

    # interact with contract
    cblbCheckinContractInstance = w3.eth.contract(address=os.getenv('CBLB_CHECKIN_CONTRACT_ADDRESS'), abi=abiCblbCheckinContract)
    currCheckinCblbAmount = cblbCheckinContractInstance.functions.getCurrentCblbAmount().call({'from': walletObj.address})
    return w3.fromWei(currCheckinCblbAmount, 'ether')
