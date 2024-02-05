import os
import time
from datetime import datetime

def logOneLine(str):
    print('[CBLB MINER]:',datetime.date(datetime.now()),':', str)
    
    todayLogFilePath = 'logs/' + datetime.date(datetime.now()).strftime("%Y-%m-%d") + '.txt'
    # log folder exist?
    isLogFolderExist = os.path.exists('logs/')
    isTodayLogFolderExist = os.path.exists(todayLogFilePath)

    structedLogs = '[CBLB MINER]: ' + datetime.now().strftime("%Y/%m/%d, %H:%M:%S, ") + str + '\n'

    if not isLogFolderExist:
        os.mkdir('logs', 0o755)
    
    if not isTodayLogFolderExist:
        with open(todayLogFilePath, 'w') as f:
            f.write(structedLogs)
    else:
        with open(todayLogFilePath, 'a') as f:
            f.write(structedLogs)

def removeExpiredLogFiles():
    logOneLine('Check if thers are any expired log files')
    # remove over 7 days logs
    currentTime = time.time()
    dayInSecond = 86400
    for f in os.listdir('logs'):
        fileLocat = os.path.join(os.getcwd(),'logs', f)
        fileTime = os.stat(fileLocat).st_mtime

        if fileTime < currentTime -dayInSecond * 7:
            logOneLine('    Remove log file: '+ f)
            os.remove(fileLocat)