import os
import json
import time
from dotenv import load_dotenv
from munch import DefaultMunch

# module
from libs import log
from libs import localDb

load_dotenv()

chainId = int(os.getenv("CHAIN_ID"))

def getMaticBalance(w3, walletObj):
    balance = w3.eth.get_balance(walletObj.address)
    return w3.fromWei(balance, 'ether')

def getCblbBalance(w3, walletObj):
    # load abi
    abiCblbTokenContract = {}
    with open('abi.json', 'r') as f:
        abiDict = json.load(f)
        abiObj = DefaultMunch.fromDict(abiDict)
        abiCblbTokenContract = abiObj.cblbTokenContractAbi
    
    # interact with contract
    cblbTokenInstance = w3.eth.contract(address=os.getenv('CBLB_TOKEN_CONTRACT_ADDRESS'), abi=abiCblbTokenContract)
    balance = cblbTokenInstance.functions.balanceOf(walletObj.address).call({'from': walletObj.address})
    return w3.fromWei(balance, 'ether')

def transferMatic(w3, walletObj, toAddress, value):
    # get txn nonce
    nonce = w3.eth.getTransactionCount(walletObj.address)
    # trasnfer txn
    storeTxn = {
        'nonce': nonce,
        'to': toAddress,
        'value': w3.toWei(str(value), 'ether'),
        'gas': 2000000,
        'gasPrice': w3.toWei('200', 'gwei'),
        'chainId': chainId,
    }

    signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=walletObj.pkey)
    sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
    txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
    log.logOneLine('Transfer ' + str(value)+' MATIC from ' + walletObj.address + ' to ' + toAddress)

def transferCblb(w3, walletObj, toAddress, value):
    # load abi
    abiCblbTokenContract = {}
    with open('abi.json', 'r') as f:
        abiDict = json.load(f)
        abiObj = DefaultMunch.fromDict(abiDict)
        abiCblbTokenContract = abiObj.cblbTokenContractAbi
    
    # get contract instance
    cblbTokenInstance = w3.eth.contract(address=os.getenv('CBLB_TOKEN_CONTRACT_ADDRESS'), abi=abiCblbTokenContract)
    # get txn nonce
    nonce = w3.eth.getTransactionCount(walletObj.address)
    # trasnfer txn
    storeTxn = cblbTokenInstance.functions.transfer(toAddress, w3.toWei(str(value), 'ether')).buildTransaction({
        'nonce': nonce,
        'from': walletObj.address,
        'chainId': chainId,
        'maxFeePerGas':w3.toWei(os.getenv('MAX_FEE_PER_GAS'), 'gwei')
    })

    signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=walletObj.pkey)
    sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
    txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
    log.logOneLine('Transfer ' + str(value)+' CBLB from ' + walletObj.address + ' to ' + toAddress)


def balanceLeaderAndMinerMatic(w3, leaderWalletObj, minersWalletArrayObj):
    log.logOneLine('-------Balance leader wallet and miners wallets MATIC-------')
    balanceLeader = localDb.getAddressMaticBalance(leaderWalletObj.address)

    # gather overflow MATIC balance from miners to leader
    for minerWalletObj in minersWalletArrayObj:
        balanceMiner = localDb.getAddressMaticBalance(minerWalletObj.address)
        
        if float(balanceMiner) > float(os.getenv('MINER_MATIC_BALANCE_MAX')) :
            log.logOneLine('Miner address ' + minerWalletObj.address + ' balance is ' + str(balanceMiner) + ' MATIC, transfer out MATIC to leader address.')
            valueTransfer = float(balanceMiner) - float(os.getenv('MINER_MATIC_BALANCE_PROPERGATE'))
            transferMatic(w3, minerWalletObj, leaderWalletObj.address, valueTransfer)

            balanceLeader = float(balanceLeader) + valueTransfer
            localDb.updateAddressMaticBalance(leaderWalletObj.address, balanceLeader)
            localDb.updateAddressMaticBalance(minerWalletObj.address, str(os.getenv('MINER_MATIC_BALANCE_PROPERGATE')))
        else:
            log.logOneLine('Miner address ' + minerWalletObj.address + ' balance is ' + str(balanceMiner) + ' MATIC, skip transfer out.')
    
    if float(balanceLeader) > float(os.getenv('LEADER_MATIC_BALANCE_PROPERGATE')):
        currBalanceLeader = float(balanceLeader)
        for minerWalletObj in minersWalletArrayObj:
            if currBalanceLeader > float(os.getenv('LEADER_MATIC_BALANCE_PROPERGATE')):
                minerBalance = localDb.getAddressMaticBalance(minerWalletObj.address)
                if float(minerBalance) < float(os.getenv('MINER_MATIC_BALANCE_MIN')):
                    transferMatic(w3, leaderWalletObj, minerWalletObj.address, float(os.getenv('MINER_MATIC_BALANCE_PROPERGATE')))
                    time.sleep(5)

                    currBalanceLeader = currBalanceLeader - float(os.getenv('MINER_MATIC_BALANCE_PROPERGATE'))
                    localDb.updateAddressMaticBalance(leaderWalletObj.address, currBalanceLeader)
                    localDb.updateAddressMaticBalance(minerWalletObj.address, float(minerBalance) + float(os.getenv('MINER_MATIC_BALANCE_PROPERGATE'))) 
                    
                else:
                    log.logOneLine('Miner address balance is ' + minerBalance + ', skip funding')
    else:
        log.logOneLine('Leader address ' + leaderWalletObj.address + ' has ' + str(balanceLeader) + ' MATIC, would not propagete to miner ')

def collectLeaderMinerCblb(w3, leaderWalletObj, minersWalletArrayObj):
    log.logOneLine('-------Collect CBLB from leader wallet and miners wallets-------')
    if os.getenv('BENEFICIARY_ADDRESS') == '':
        log.logOneLine('Beneficiary address is empty, can NOT collect CBLB')
        log.logOneLine('Please config BENEFICIARY_ADDRESS variable value in .env file to set beneficiary address')
    else:
        collectWalletCblb(w3, leaderWalletObj)
        time.sleep(1)
        for minerWalletObj in minersWalletArrayObj:
            collectWalletCblb(w3, minerWalletObj)
            time.sleep(1)

def collectWalletCblb(w3, walletObj):
    if os.getenv('BENEFICIARY_ADDRESS') == walletObj.address:
        log.logOneLine('Beneficiary address is self, skip collect')
    else:
        balanceWallet = localDb.getAddressCblbBalance(walletObj.address)
        if float(balanceWallet) > float(os.getenv('CBLB_COLLECT_THRESHOLD')):
            transferCblb(w3, walletObj, os.getenv('BENEFICIARY_ADDRESS'), balanceWallet)
            localDb.updateAddressCblbBalance(walletObj.address, '0')
        else:
            log.logOneLine('Wallet address ' + walletObj.address + ' has ' + str(balanceWallet) + ' CBLB, within collect threshold ' + os.getenv('CBLB_COLLECT_THRESHOLD') + ', skip collect')
        
def waitFundLoop(w3, leaderWalletObj):
    log.logOneLine('Please fund MATIC to leader address ' + leaderWalletObj.address)
    balanceLeader = getMaticBalance(w3, leaderWalletObj)

    while float(balanceLeader) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
        

        log.logOneLine('Leader wallet MATIC balance is ' + str(balanceLeader) + ', unsuffi min checkin require balance ' + os.getenv('CHECKIN_MATIC_BALANCE_MIN') + ' MATIC')
        log.logOneLine('Recommand funding ' + str(
            float(os.getenv('LEADER_MATIC_BALANCE_PROPERGATE')) + 
            float(os.getenv('MINER_NUMBER')) * 
            float(os.getenv('MINER_MATIC_BALANCE_PROPERGATE'))
            ) + ' MATIC to leader address ' + leaderWalletObj.address + ' make ' + os.getenv('MINER_NUMBER') + ' mining'
        )
        log.logOneLine('Scan qrcode below to fund leader address ' + leaderWalletObj.address + ' fund MATIC')
        os.system("qr " + leaderWalletObj.address)
        log.logOneLine('Waiting 3 mins recheck leader wallet MATIC balance')
        time.sleep(3 * 60)
        balanceLeader = getMaticBalance(w3, leaderWalletObj)