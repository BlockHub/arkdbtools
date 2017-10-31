from collections import namedtuple
import copy
from .config import *


def get_transactionlist(cursor, pubkey):
    """returns a list of named tuples of all transactions relevant to a specific delegates voters.
    Flow: finds all voters, SELECTs all transactions of those voters, names all transactions according to
    the scheme: 'transaction', 'id amount timestamp recipientId senderId rawasset type fee'"""
    qry = cursor.execute_and_fetchall("""
        SELECT transactions."id", transactions."amount",
               transactions."timestamp", transactions."recipientId",
               transactions."senderId", transactions."rawasset",
               transactions."type", transactions."fee"
        FROM transactions
        WHERE transactions."senderId" IN
          (SELECT transactions."recipientId"
           FROM transactions, votes
           WHERE transactions."id" = votes."transactionId"
           AND votes."votes" = '+{0}')
        OR transactions."recipientId" IN
          (SELECT transactions."recipientId"
           FROM transactions, votes
           WHERE transactions."id" = votes."transactionId"
           AND votes."votes" = '+{0}')
        ORDER BY transactions."timestamp" ASC;""".format(pubkey))

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
    qry = cursor.execute_and_fetchall("""
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
    qry = cursor.execute_and_fetchall("""
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
    qry = cursor.execute_and_fetchall("""
            SELECT transactions."recipientId", max(transactions."timestamp")
            FROM transactions
            WHERE transactions."senderId" = '{}'
            GROUP BY transactions."recipientId"
            """.format(address))
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


def cal_share(balance_dict, block, chunk_dict, reuse):
    """calculates pool balances and share per voter at a given state.
    chunk_dict and reuse are used to remember the result of previous calculation,
    making sure you don't need to recalculate a block if no transactions occurred between
    2 forged blocks. (dramatically speeds up parsing time)"""

    if reuse:
        for i in chunk_dict:
            try:
                balance_dict[i]['share'] += chunk_dict[i]
            except Exception:
                pass
        return balance_dict, chunk_dict

    pool_balance = 0
    blockshare = 0
    for address in balance_dict:
        if balance_dict[address]['status'] and address not in BLACKLIST:
            pool_balance += balance_dict[address]['balance']
    for address in balance_dict:
        if balance_dict[address]['status'] and address not in BLACKLIST and\
        balance_dict[address]['last_payout'] < block.timestamp:
            blockshare = (balance_dict[address]['balance'] / pool_balance) * 2
            balance_dict[address]['share'] += blockshare
        chunk_dict.update({address: blockshare})

    return balance_dict, chunk_dict


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