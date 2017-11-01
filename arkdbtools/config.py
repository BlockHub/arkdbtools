MIN_SEC = 60
HOUR_SEC = MIN_SEC * 60
DAY_SEC = HOUR_SEC * 24
WEEK_SEC = DAY_SEC * 7

# a month is obviously a fucked up concept conceived by the devil,
# so we use 30 day intervals
MONTH_SEC = 30 * DAY_SEC



CONNECTION = {
    'HOST'    : "localhost",
    'DATABASE': "ark_mainnet",
    'USER'    : None,
    'PASSWORD': None,
    }

DELEGATE = {
    'ADDRESS': None,
    'PUBKEY':  None,
    'SECRET':  None
}

ARK = 100000000
TX_FEE = 10000000

CALCULATION_SETTINGS = {'BLACKLIST': [],
                        'EXCEPTIONS': {'address': {'replace': 'int else None'}},
                        'MAX': float('inf'),
                        'SHARE_FEES': False,
}

SENDER_SETTINGS = {
    'DEFAULT_SHARE': 0.95,
    'COVER_FEES': False,
    'SHARE_PERCENTAGE_EXCEPTIONS': {
        'address': 0.8,
        },
    'TIMESTAMP_BRACKETS': {
         float('inf'): 0.95,
         16247647    : 0.96
         },
    'MIN_PAYOUT_DAILY': 2 * ARK,
    'MIN_PAYOUT_WEEKLY': 0.1 * ARK,
    # don't put this at 0, because wallets abandoned wallets will
    # keep accruing a small balance
    'MIN_PAYOUT_MONTHLY': 0.0001 * ARK,
    # 0 is monday. 6 is sunday
    'DAY_WEEKLY_PAYOUT': 5,
    'DAY_MONTHLY_PAYOUT': 24,
    'PAYOUTSENDER_TEST': True

}


LOGGING = {
    # log to this file and create -1, -2 etc. for historical versions
    'logfile'  : '/tmp/ark.log',
    # debugging: on or off
    'verbosity': True,
    # max size of the logfile before it gets rotated to <file>-1
    'maxsize'  : 1024 * 1024
}
