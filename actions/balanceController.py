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

def getMaticBalance(w3, address):
    balance = w3.eth.get_balance(address)
    return w3.fromWei(balance, 'ether')

def getCblbBalance(w3, address):
    # load abi
    abiCblbTokenContract = {}
    with open('abi.json', 'r') as f:
        abiDict = json.load(f)
        abiObj = DefaultMunch.fromDict(abiDict)
        abiCblbTokenContract = abiObj.cblbTokenContractAbi
    
    # interact with contract
    cblbTokenInstance = w3.eth.contract(address=os.getenv('CBLB_TOKEN_CONTRACT_ADDRESS'), abi=abiCblbTokenContract)
    balance = cblbTokenInstance.functions.balanceOf(address).call({'from': address})
    return w3.fromWei(balance, 'ether')

def transferMatic(w3, walletObj, toAddress, value):
    # get txn nonce
    nonce = w3.eth.getTransactionCount(walletObj.address)
    # get gas price
    gasPriceWei = w3.eth.gas_price
    gasPrice = w3.fromWei(gasPriceWei, 'gwei')
    # trasnfer txn
    storeTxn = {
        'nonce': nonce,
        'to': toAddress,
        'value': w3.toWei(str(value), 'ether'),
        'gas': 21000,
        'gasPrice': gasPriceWei,
        'chainId': chainId,
    }

    signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=walletObj.pkey)
    sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
    txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
    log.logOneLine('Transfer ' + str(value)+' MATIC from ' + walletObj.address + ' to ' + toAddress)
    while nonce == w3.eth.getTransactionCount(walletObj.address):
        time.sleep(1)

def collectMiniMaticToLeaderWallet(w3, leaderWalletObj, minersWalletArrayObj):
    log.logOneLine('Miners small amout to checker')

    for minerWalletObj in minersWalletArrayObj:
        balanceMaticMiner = localDb.getAddressMaticBalance(minerWalletObj.address)
        balanceCblbMiner = localDb.getAddressCblbBalance(minerWalletObj.address)

        if float(balanceMaticMiner) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')) and float(balanceMaticMiner) > 0 and float(balanceCblbMiner) == 0:

            gasAmount = 21000
            # get txn nonce
            nonce = w3.eth.getTransactionCount(minerWalletObj.address)
            # get gas price
            gasPriceWei = w3.eth.gas_price
            # get walletObj MATIC balance
            matic = getMaticBalance(w3, minerWalletObj.address)
            maticWei = w3.toWei(matic, 'ether')

            exactValueWei = int(maticWei) - gasAmount * int(gasPriceWei)
            if int(maticWei) > gasAmount * int(gasPriceWei):

                exactValue = w3.fromWei(exactValueWei, 'ether')
                exactValueFloat = float(exactValue)

                # trasnfer txn
                storeTxn = {
                    'nonce': nonce,
                    'to': leaderWalletObj.address,
                    'value': exactValueWei,
                    'gas': gasAmount,
                    'gasPrice': gasPriceWei,
                    'chainId': chainId,
                }

                signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=minerWalletObj.pkey)
                sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
                txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
                
                log.logOneLine('Transfer ' + str(exactValueFloat)+ ' MATIC from ' + minerWalletObj.address + ' to leader ' + leaderWalletObj.address)
                while nonce == w3.eth.getTransactionCount(minerWalletObj.address):
                    time.sleep(1)

def collectMiniMaticToAddress(w3, walletObj, toAddress):
    gasAmount = 21000
    # get txn nonce
    nonce = w3.eth.getTransactionCount(walletObj.address)
    # get gas price
    gasPriceWei = w3.eth.gas_price
    # get walletObj MATIC balance
    matic = getMaticBalance(w3, walletObj.address)
    maticWei = w3.toWei(matic, 'ether')

    exactValueWei = int(maticWei) - gasAmount * int(gasPriceWei)
    if int(maticWei) > gasAmount * int(gasPriceWei):

        exactValue = w3.fromWei(exactValueWei, 'ether')
        exactValueFloat = float(exactValue)

        # trasnfer txn
        storeTxn = {
            'nonce': nonce,
            'to': toAddress,
            'value': exactValueWei,
            'gas': gasAmount,
            'gasPrice': gasPriceWei,
            'chainId': chainId,
        }

        signedStoreTxn = w3.eth.account.sign_transaction(storeTxn, private_key=walletObj.pkey)
        sendStoreTxn = w3.eth.send_raw_transaction(signedStoreTxn.rawTransaction)
        txReceipt = w3.eth.wait_for_transaction_receipt(sendStoreTxn)
                
        log.logOneLine('Transfer ' + str(exactValueFloat)+ ' MATIC from ' + walletObj.address + ' to address ' + toAddress)
        while nonce == w3.eth.getTransactionCount(walletObj.address):
            time.sleep(1)

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
    # get gas price
    gasPrice = w3.eth.gas_price
    # trasnfer txn
    storeTxn = cblbTokenInstance.functions.transfer(toAddress, w3.toWei(str(value), 'ether')).buildTransaction({
        'nonce': nonce,
        'from': walletObj.address,
        'chainId': chainId,
        'maxFeePerGas': w3.toWei(gasPrice * 1.5, 'wei') 
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
        balanceCblb = localDb.getAddressCblbBalance(walletObj.address)
        balanceMatic = localDb.getAddressMaticBalance(walletObj.address)

        if float(balanceCblb) > float(os.getenv('CBLB_COLLECT_THRESHOLD')) and float(balanceMatic) > float(os.getenv('COLLECT_MATIC_BALANCE_MIN')):
            transferCblb(w3, walletObj, os.getenv('BENEFICIARY_ADDRESS'), balanceCblb)
            localDb.updateAddressCblbBalance(walletObj.address, '0')
        elif float(balanceCblb) > 0 and float(balanceMatic) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')) and float(balanceMatic) > float(os.getenv('COLLECT_MATIC_BALANCE_MIN')):
            transferCblb(w3, walletObj, os.getenv('BENEFICIARY_ADDRESS'), balanceCblb)
            localDb.updateAddressCblbBalance(walletObj.address, '0')
        else:
            log.logOneLine('Wallet address ' + walletObj.address + ' has ' + str(balanceCblb) + ' CBLB, skip collect')
        
def waitFundLoop(w3, leaderWalletObj):
    balanceLeader = getMaticBalance(w3, leaderWalletObj.address)
    if float(balanceLeader) < float(os.getenv('CHECKIN_MATIC_BALANCE_MIN')):
        log.logOneLine('Collect leader wallet MATIC to BENEFICIARY')
        collectMiniMaticToAddress(w3, leaderWalletObj, os.getenv('BENEFICIARY_ADDRESS'))

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
        balanceLeader = getMaticBalance(w3, leaderWalletObj.address)