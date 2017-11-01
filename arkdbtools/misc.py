import logging
import arkdbtools

from arkdbtools import dbtools, config

if __name__ == '__main__':

    dbtools.set_delegate(
        address='AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE',
        pubkey='0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a')

    dbtools.set_connection(
        host='localhost',
        database='ark_mainnet',
        user='ark')

    print('starting')
    payouts, timestamp = dbtools.Delegate.share()
    for i in payouts:
        print(i, payouts[i])