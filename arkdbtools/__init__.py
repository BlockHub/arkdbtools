from .config import *
import psycopg2
from arky import api, core
from .utils import *
from .share_calculator import *
import binascii
import datetime

class ApiError(Exception):
    pass


class NodeDbError(Exception):
    pass


def set_connection(host=None, database=None, user=None, password=None):
    """Set connection parameters. Call set_connection with no arguments to clear."""
    config.CONNECTION['HOST'] = host
    config.CONNECTION['DATABASE'] = database
    config.CONNECTION['USER'] = user
    config.CONNECTION['PASSWORD'] = password


def set_delegate(address=None, pubkey=None, secret=None):
    """Set delegate parameters. Call set_delegate with no arguments to clear."""
    config.DELEGATE['ADDRESS'] = address
    config.DELEGATE['PUBKEY'] = pubkey
    config.DELEGATE['SECRET'] = secret

class DbConnection:
    def __init__(self):
        self._conn = psycopg2.connect(host=config.CONNECTION['HOST'],
                                      database=config.CONNECTION['DATABASE'],
                                      user=config.CONNECTION['USER'],
                                      password=config.CONNECTION['PASSWORD'])

    def connection(self):
        return self._conn


class DbCursor:
    def __init__(self, dbconnection=None):
        if not dbconnection:
            dbconnection = DbConnection()
        self._cur = dbconnection.connection().cursor()

    def execute(self, qry, *args):
        self._cur.execute(qry, *args)

    def fetchall(self):
        return self._cur.fetchall()

    def fetchone(self):
        return self._cur.fetchone()

    def execute_and_fetchall(self, qry, *args):
        self.execute(qry, *args)
        return self._cur.fetchall()

    def execute_and_fetchone(self, qry, *args):
        self.execute(qry, *args)
        return self._cur.fetchone()


class Blockchain():
    @staticmethod
    def height(redundancy=3):
        height = []
        function = api.Block.getBlockchainHeight
        for i in range(redundancy):
            try:
                api.use('ark')
                height.append(api_call(function)['height'])
            except Exception:
                pass

        if not height:
            raise ApiError(
                'Could not get a result through '
                'api for {0}, with redundancy: {1}'.format(function, redundancy)
            )
        return max(height)


class Node:
    @staticmethod
    def height():
        cursor = DbCursor()
        return cursor.execute_and_fetchone("""
                            SELECT max(blocks."height") 
                            FROM blocks
        """)[0]

    @staticmethod
    def check_node(max_difference):
        if Blockchain.height() - Node.height() <= max_difference:
                return True
        else:
            return False

    @staticmethod
    def max_timestamp():
        # Fetch the max timestamp as it occurs in table blocks, or return
        # a previously cached value.
        cursor = DbCursor()

        r = cursor.execute_and_fetchone("""
                SELECT max(timestamp) 
                FROM blocks
        """)[0]
        if not r:
            raise NodeDbError('failed to get max timestamp from node')
        return r


class Address:
    @staticmethod
    def transactions(address):
        """Returns a list of named tuples of all transactions for an address.
        Scheme:
        'transaction',
            'id amount timestamp recipientId senderId rawasset type fee'"""
        cursor = DbCursor()
        qry = cursor.execute_and_fetchall("""
        SELECT transactions."id", transactions."amount",
               transactions."timestamp", transactions."recipientId",
               transactions."senderId", transactions."rawasset",
               transactions."type", transactions."fee"
        FROM transactions
        WHERE transactions."senderId" = '{0}'
        OR transactions."recipientId" = '{0}'
        ORDER BY transactions."timestamp" ASC""".format(address))

        Transaction = namedtuple(
            'transaction',
            'id amount timestamp recipientId senderId rawasset type fee')
        named_transactions = []

        for i in qry:
            tx_id = Transaction(
                id=i[0],
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

    @staticmethod
    def votes(address):
        """Returns a map all votes made by an address, {(+/-)pubkeydelegate:timestamp}"""

        cursor = DbCursor()
        qry = cursor.execute_and_fetchall("""
           SELECT votes."votes", transactions."timestamp"
           FROM votes, transactions
           WHERE transactions."id" = votes."transactionId"
           AND transactions."recipientId" = '{}'
        """.format(address))
        res = {}
        for i in qry:
            res.update({i[0]: i[1]})
        return res

    @staticmethod
    def balance(address):
        """Takes a single address and returns the current balance.
        """
        txhistory = Address.transactions(address)
        balance = 0
        for i in txhistory:
            if i.recipientId == address:
                balance += i.amount
            if i.senderId == address:
                balance -= (i.amount + i.fee)

        delegates = Delegate.delegates()
        for i in delegates:
            if address == i.address:
                forged_blocks = Delegate.blocks(i.pubkey)
                for block in forged_blocks:
                    balance += (block.reward + block.totalFee)
        return balance


class Delegate:
    @staticmethod
    def delegates():
        """returns a list of named tuples of all delegates.
        {username: {'pubkey':pubkey, 'timestamp':timestamp, 'address':address}}"""
        cursor = DbCursor()
        qry = cursor.execute_and_fetchall("""
            SELECT delegates."username", delegates."transactionId", transactions."timestamp", transactions."senderId", 
            transactions."senderPublicKey" 
            FROM transactions
            JOIN delegates ON transactions."id" = delegates."transactionId"
        """)

        Delegate = namedtuple(
            'delegate',
            'username pubkey timestamp address transactionId')
        res = []
        for i in qry:
            registration = Delegate(
                username=i[0],
                pubkey=binascii.hexlify(i[4]).decode("utf-8"),
                timestamp=i[2],
                address=i[3],
                transactionId=i[1]
            )
            res.append(registration)
        return res


    @staticmethod
    def lastpayout(delegate_address, blacklist=[]):
        '''
        Assumes that all send transactions from a delegate are payouts.
        Use blacklist to remove rewardwallet and other transactions if the
        address is not a voter. blacklist can contain both addresses and transactionIds'''
        cursor = DbCursor()

        if len(blacklist) > 1:
            command_blacklist = 'NOT IN ' + str(tuple(blacklist))
        elif len(blacklist) == 1:
            command_blacklist = '!= ' + "'" + blacklist[0] + "'"
        else:
            command_blacklist = "!= 'nothing'"
        qry = cursor.execute_and_fetchall("""
                    SELECT ts."recipientId", ts."id", ts."timestamp"
                    FROM transactions ts,
                      (SELECT MAX(transactions."timestamp") AS max_timestamp, transactions."recipientId"
                       FROM transactions
                       WHERE transactions."senderId" = '{0}'
                       AND transactions."id" {1}
                       GROUP BY transactions."recipientId") maxresults
                    WHERE ts."recipientId" = maxresults."recipientId"
                    AND ts."timestamp"= maxresults.max_timestamp;

                    """.format(delegate_address, command_blacklist))
        result = []

        Payout = namedtuple(
            'payout',
            'address  id timestamp')

        for i in qry:
            payout = Payout(
                address=i[0],
                id=i[1],
                timestamp=i[2]
            )
            result.append(payout)
        return result

    @staticmethod
    def votes(delegate_pubkey):
        """returns every address that has voted for a delegate.
        Current voters can be obtained using voters"""
        cursor = DbCursor()

        qry = cursor.execute_and_fetchall("""
                 SELECT transactions."recipientId", transactions."timestamp"
                 FROM transactions, votes
                 WHERE transactions."id" = votes."transactionId"
                 AND votes."votes" = '+{}';
        """.format(delegate_pubkey))

        Voter = namedtuple(
            'voter',
            'address timestamp')
        voters = []
        for i in qry:
            voter = Voter(
                address=i[0],
                timestamp=i[1]
                          )
            voters.append(voter)
        return voters

    @staticmethod
    def unvotes(delegate_pubkey):
        cursor = DbCursor()

        qry = cursor.execute_and_fetchall("""
                         SELECT transactions."recipientId", transactions."timestamp"
                         FROM transactions, votes
                         WHERE transactions."id" = votes."transactionId"
                         AND votes."votes" = '-{}';
                """.format(delegate_pubkey))

        Voter = namedtuple(
            'voter',
            'address timestamp')

        unvoters = []
        for i in qry:
            unvoter = Voter(
                address=i[0],
                timestamp=i[1]
            )
            unvoters.append(unvoter)
        return unvoters

    @staticmethod
    def voters(delegate_pubkey=None):
        if not delegate_pubkey:
            delegate_pubkey = DELEGATE['PUBKEY']
        votes = Delegate.votes(delegate_pubkey)
        unvotes = Delegate.unvotes(delegate_pubkey)
        for count, i in enumerate(votes):
            for x in unvotes:
                if i.address == x.address and i.timestamp < x.timestamp:
                    del votes[count]
        return votes

    @staticmethod
    def blocks(delegate_pubkey=None, max_timestamp=None):
        """returns a list of named tuples of all blocks forged by a delegate.
        if delegate_pubkey is not specified, set_delegate needs to be called in advance.
        max_timestamp can be configured o retrieve blocks up to a certain timestamp."""

        if not delegate_pubkey:
            delegate_pubkey = DELEGATE['PUBKEY']
        if max_timestamp:
            max_timestamp_sql = """ blocks."timestamp" <= {} AND""".format(max_timestamp)
        else:
            max_timestamp_sql = ''
        cursor = DbCursor()

        qry = cursor.execute_and_fetchall("""
             SELECT blocks."timestamp", blocks."height", blocks."id", blocks."totalFee", blocks."reward"
             FROM blocks
             WHERE {0} blocks."generatorPublicKey" = '\\x{1}'
             ORDER BY blocks."timestamp" 
             ASC""".format(
            max_timestamp_sql,
            delegate_pubkey))

        Block = namedtuple('block',
                           'timestamp height id totalFee reward')
        block_list = []
        for block in qry:
            block_value = Block(timestamp=block[0],
                                height=block[1],
                                id=block[2],
                                totalFee=block[3],
                                reward=block[4])
            block_list.append(block_value)

        return block_list

    @staticmethod
    def share(passphrase=None, last_payout=None, start_block=0):
        """Calculate the true blockweight payout share for a given delegate,
        assuming no exceptions were made for a voter. last_payout is a map of addresses and timestamps:
        {address: timestamp}. If no argument are given, it will start the calculation at the first forged block
        by the delegate, generate a last_payout from transaction history, and use the set_delegate info.

        If a passphrase is provided, it is only used to generate the adddress and keys, no transactions are sent.
        (Still not recommended unless you know what you are doing, version control could store your passphrase for example;
        very risky)
        """

        #todo allow last_payout to be a single int, add blacklisting settings and max balance for calculations.
        cursor = DbCursor()

        if passphrase:
            delegate_keys = core.getKeys(secret=passphrase,
                                         network='ark',
                                        )

            delegate_pubkey = delegate_keys.public
            delegate_address = core.getAddress(keys=delegate_keys)
        else:
            delegate_pubkey = config.DELEGATE['PUBKEY']
            delegate_address = config.DELEGATE['ADDRESS']

        max_timestamp = Node.max_timestamp()

        # utils function
        transactions = get_transactionlist(
                            cursor=cursor,
                            pubkey=delegate_pubkey)

        votes = Delegate.votes(delegate_pubkey)

        if not last_payout:
            last_payout = Delegate.lastpayout(delegate_address)

        # create a map of voters
        voter_dict = {}
        for voter in votes:
            voter_dict.update({voter.address: {'balance': 0.0,
                                               'status': False,
                                               'last_payout': voter.timestamp,
                                               'share': 0.0,
                                               'vote_timestamp': voter.timestamp,
                                               'blocks_forged': []}})

        # check if a voter is/used to be a forging delegate
        delegates = Delegate.delegates()
        for i in delegates:
            if i.address in voter_dict:
                voter_dict[i.address]['blocks_forged'].extend(Delegate.blocks(i.pubkey))

        try:
            for i in config.CALCULATION_SETTINGS['blacklist']:
                voter_dict.pop(i)
        except Exception:
            pass

        # update the last_payout.
        for payout in last_payout:
            try:
                voter_dict[payout.address]['last_payout'] = payout.timestamp
            except Exception:
                pass


        # get all forged blocks of delegate:
        blocks = Delegate.blocks(max_timestamp=max_timestamp)

        block_nr = start_block
        chunk_dict = {}
        reuse = False
        for tx in transactions:
            while tx.timestamp > blocks[block_nr].timestamp:
                if reuse:
                    block_nr +=1
                    for x in chunk_dict:
                        voter_dict[x]['share'] += chunk_dict[x]
                    continue
                block_nr += 1
                poolbalance = 0
                chunk_dict = {}
                for i in voter_dict:
                    balance = voter_dict[i]['balance']
                    if voter_dict[i]['balance'] > config.CALCULATION_SETTINGS['max']:
                        balance = config.CALCULATION_SETTINGS['max']
                    if i in config.CALCULATION_SETTINGS['exceptions']:
                        balance = config.CALCULATION_SETTINGS['exceptions'][i]

                    if voter_dict[i]['blocks_forged']:
                        for x in voter_dict[i]['blocks_forged']:
                            if x.timestamp < blocks[block_nr].timestamp:
                                voter_dict[i]['balance'] += (x.reward + x.totalFee)
                                voter_dict[i]['blocks_forged'].remove(x)
                    if voter_dict[i]['status']:
                        if not voter_dict[i]['balance'] < 0:
                            poolbalance += balance
                        else:
                            raise Exception('balance lower than zero for: {0}'.format(i))
                for i in voter_dict:
                    balance = voter_dict[i]['balance']

                    if voter_dict[i]['balance'] > config.CALCULATION_SETTINGS['max']:
                        balance = config.CALCULATION_SETTINGS['max']
                    if i in config.CALCULATION_SETTINGS['exceptions']:
                        balance = config.CALCULATION_SETTINGS['exceptions'][i]

                    if voter_dict[i]['status'] and voter_dict[i]['last_payout'] < blocks[block_nr].timestamp:
                        if config.CALCULATION_SETTINGS['share_fees']:
                            share = (balance/poolbalance) * (blocks[block_nr].reward +
                                                             blocks[block_nr].totalFee)
                        else:
                            share = (balance/poolbalance) * blocks[block_nr].reward
                        voter_dict[i]['share'] += share
                        chunk_dict.update({i: share})
                reuse = True


            # parsing a transaction
            minvote = '{{"votes":["-{0}"]}}'.format(delegate_pubkey)
            plusvote = '{{"votes":["+{0}"]}}'.format(delegate_pubkey)

            reuse = False

            if tx.recipientId in voter_dict:
                voter_dict[tx.recipientId]['balance'] += tx.amount
            if tx.senderId in voter_dict:
                voter_dict[tx.senderId]['balance'] -= (tx.amount + tx.fee)
            if tx.senderId in voter_dict and tx.type == 3 and plusvote in tx.rawasset:
                voter_dict[tx.senderId]['status'] = True
            if tx.senderId in voter_dict and tx.type == 3 and minvote in tx.rawasset:
                voter_dict[tx.senderId]['status'] = False

        remaining_blocks = len(blocks) - block_nr
        for i in range(remaining_blocks):
            for x in chunk_dict:
                voter_dict[x]['share'] += chunk_dict[x]
        return voter_dict, max_timestamp


class Core:

    @staticmethod
    def send(address, amount, smartbridge, network='ark', secret=config.DELEGATE['SECRET']):
        api.use(network)
        tx = core.Transaction(amount=amount, recipientId=address)
        tx.sign(secret)
        tx.serialize()
        for i in range(5):
            result = api.sendTx(tx)
            if result['success']:
                return True

        raise Exception('failed to send transaction 5 times, response: {}'.format(result))

    @staticmethod
    def send_transaction(data, frq_dict, max_timestamp):
        # data[0] is always the address.
        # data[1] is a map having keys
        #         last_payout, status, share and vote_timestamp.

        day_month = datetime.datetime.today().month
        day_week = datetime.datetime.today().weekday()
        address = data[0]
        amount = 0
        if config.SHARE['COVER_TX_FEES']:
            fees = 0
            del_fees = config.SHARE['FEES']
        else:
            fees = config.SHARE['FEES']
            del_fees = 0
        if address in config.EXCEPTIONS:
            amount = ((data[1]['share'] * config.EXCEPTIONS[address]) - fees)
        else:
            if config.SHARE['TIMESTAMP_BRACKETS']:
                for i in config.SHARE['TIMESTAMP_BRACKETS']:
                    if data[1]['vote_timestamp'] < i:
                        amount = ((data[1]['share'] *
                                   config.SHARE['TIMESTAMP_BRACKETS'][i])
                                  - fees)
            else:
                amount = ((data[1]['share'] *
                           config.SHARE['DEFAULT_SHARE'])
                          - fees)

        delegate_share = data[1]['share'] - (amount + del_fees)
        rl.debug('delegateshare for {}: {}'.format(data[0], delegate_share))
        if address in frq_dict:
            frequency = frq_dict[address]
        else:
            frequency = 2

        if frequency == 1:
            if data[1]['last_payout'] < max_timestamp - (3600 * 20):
                if amount > config.SHARE['MIN_PAYOUT_BALANCE_DAILY']:
                    result = send(address, amount)
                    return result, delegate_share, amount

        elif frequency == 2 and day_week == 5:
            if data[1]['last_payout'] < max_timestamp - (3600 * 24):
                if amount > config.SHARE['MIN_PAYOUT_BALANCE_WEEKLY']:
                    result = send(address, amount)
                    return result, delegate_share, amount

        elif frequency == 3 and day_month == 28:
            if data[1]['last_payout'] < max_timestamp - (3600 * 24 * 24):
                if amount > config.SHARE['MIN_PAYOUT_BALANCE_MONTHLY']:
                    result = send(address, amount)
                    return result, delegate_share, amount
        return None, 0