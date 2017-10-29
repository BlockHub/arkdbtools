from collections import namedtuple
import copy
from .config import *


def get_transactionlist(cursor, max_timestamp, pubkey):
    qry = cursor.execute_and_fetch_all("""
        SELECT transactions."id", transactions."amount",
               transactions."timestamp", transactions."recipientId",
               transactions."senderId", transactions."rawasset",
               transactions."type", transactions."fee"
        FROM transactions
        WHERE transactions."timestamp" <= {0}
        AND transactions."senderId" IN
          (SELECT transactions."recipientId"
           FROM transactions, votes
           WHERE transactions."id" = votes."transactionId"
           AND votes."votes" = '+{1}')
        OR transactions."recipientId" IN
          (SELECT transactions."recipientId"
           FROM transactions, votes
           WHERE transactions."id" = votes."transactionId"
           AND votes."votes" = '+{1}')
        ORDER BY transactions."timestamp" ASC;""".format(
            max_timestamp,
            pubkey))

    def name_transactionslist(transactions):
        Transaction = namedtuple(
            'transaction',
            'id amount timestamp recipientId senderId rawasset type fee')
        named_transactions = []
        for i in transactions:
            tx_id = Transaction(id=i[0],
                                amount=i[1],
                                timestamp=i[2],
                                recipientId=i[3],
                                senderId=i[4],
                                rawasset=i[5],
                                type=i[6],
                                fee=i[7],
                                )

            named_transactions.append(tx_id)
        return named_transactions
    return name_transactionslist(qry)


def get_all_voters(cursor, max_timestamp, pubkey):
    qry = cursor.execute_and_fetch_all("""
                 SELECT transactions."recipientId", transactions."timestamp"
                 FROM transactions, votes
                 WHERE transactions."timestamp" <= {0}
                 AND transactions."id" = votes."transactionId"
                 AND votes."votes" = '+{1}';""".format(
                     max_timestamp,
                     pubkey))

    def create_voterdict(res):
        voter_dict = {}
        for i in res:
            voter_dict.update({i[0]:{'balance': 0,
                                     'status': False,
                                     'last_payout': i[1],
                                     'share': 0,
                                     'vote_timestamp': i[1]}})

        # len(res) != len(voterdict) because some people have unvoted and revoted
        # (and keys need to be hashable)
        return voter_dict
    return create_voterdict(qry)


def get_blocks(cursor, max_timestamp, pubkey):
    qry = cursor.execute_and_fetch_all("""
                SELECT blocks."timestamp", blocks."height", blocks."id"
                 FROM blocks
                 WHERE blocks."timestamp" <= {0}
                 AND blocks."generatorPublicKey" = '\\x{1}'
                 ORDER BY blocks."timestamp" ASC""".format(
                    max_timestamp,
                    pubkey))

    def name_blocks(qry):
        Block = namedtuple('block',
                           'timestamp height id')
        block_list = []
        for block in qry:
            block_value = Block(timestamp=block[0],
                                height=block[1],
                                id=block[2],)
            block_list.append(block_value)
        return block_list

    return name_blocks(qry)


def get_last_payout(cursor, address):
    qry = cursor.execute_and_fetch_all("""
            SELECT transaction."recipientId", max(transaction."timestamp")
            FROM transactions
            WHERE transaction."senderId" = '{}'""".format(address))
    result = {}
    for i in qry:
        result.update({i[0]: i[1]})
    return result


def parse(tx, dict, address, pubkey):
    if tx.recipientId in dict and tx.type == 0:
        dict[tx.recipientId]['balance'] += tx.amount
    if tx.senderId in dict and tx.type == 0:
        dict[tx.senderId]['balance'] -= (tx.amount + tx.fee)
    if tx.senderId in dict and tx.type == 2 or tx.type == 3:
        dict[tx.senderId]['balance'] -= tx.fee

    minvote  = '{{"votes":["-{0}"]}}'.format(pubkey)
    plusvote = '{{"votes":["+{0}"]}}'.format(pubkey)
    if tx.type == 3 and minvote in tx.rawasset:
        dict[tx.recipientId]['status'] = False
    if tx.type == 3 and plusvote in tx.rawasset:
        dict[tx.recipientId]['status'] = True
        dict[tx.recipientId]['vote_timestamp'] = tx.timestamp

    if tx.senderId == address:
        dict[tx.recipientId]['last_payout'] = tx.timestamp
    return dict


def parse_tx(all_tx, voter_dict, blocks, address, pubkey):
    balance_dict = {}
    block_nr = 0
    for tx in all_tx:
        if tx.timestamp >= blocks[block_nr].timestamp:
            res = copy.deepcopy(voter_dict)
            balance_dict.update({blocks[block_nr].timestamp: res})
            block_nr += 1
        voter_dict = parse(tx, voter_dict, address, pubkey)
    return balance_dict


def cal_share(balance_dict, last_payout, tx):
    # calculating total pool_balance and relative share per voter
    # this part could also be performed in parse_tx
    pool_balance = 0
    for address in balance_dict:
        if (balance_dict[address]['status'] and
        address not in BLACKLIST):
                pool_balance += balance_dict[address]['balance']
        for address in balance_dict:
            if (balance_dict[address]['status'] and
            address not in BLACKLIST and
            last_payout[address] < tx.timestamp):
                balance_dict[address]['share'] += (
                    balance_dict[address]['balance'] / pool_balance)
    return balance_dict


def stretch(dict, blocks):
    # duplicating block_dicts where there were no voter transactions during
    # 6.8 minute interval
    # this makes len(payout_dict) = len(blocks)
    temp_dic = {}
    last_block = min(dict.keys())

    for block in blocks:
        if block.timestamp not in dict.keys():
            temp_dic.update({block.timestamp: dict[last_block]})
        elif block.timestamp in dict.keys():
            last_block = block.timestamp

    dict.update(temp_dic)

    return dict