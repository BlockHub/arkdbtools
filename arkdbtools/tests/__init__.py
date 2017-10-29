from .config import *
import psycopg2
from arky import api, core
from .utils import *
from .share_calculator import *

class ApiError(Exception):
    pass


class NodeDbError(Exception):
    pass


def set_connection(host=None, database=None, user=None, password=None):
    config.CONNECTION['HOST'] = host
    config.CONNECTION['DATABASE'] = database
    config.CONNECTION['USER'] = user
    config.CONNECTION['PASSWORD'] = password



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
        """)[0][0]

    @staticmethod
    def check_node(max_difference):
        if Node.height() - Blockchain.height() <= max_difference:
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
        """)[0][0]
        if not r:
            raise NodeDbError('failed to get max timestamp from node')
        return r


class Delegate:
    @staticmethod
    def voters(delegate_pubkey):
        cursor = DbCursor

        qry = cursor.execute_and_fetchall("""
                 SELECT transactions."recipientId", transactions."timestamp"
                 FROM transactions, votes
                 WHERE transactions."id" = votes."transactionId"
                 AND votes."votes" = '+{}';
        """.format(delegate_pubkey))
        return qry

    @staticmethod
    def blocks():
        pass

    @staticmethod
    def share(passphrase=None, last_payout=None):
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

        transactions = get_transactionlist(
                            cursor=cursor,
                            max_timestamp=max_timestamp,
                            pubkey=delegate_pubkey)

        voters = get_all_voters(
            cursor=cursor,
            max_timestamp=max_timestamp,
            pubkey=delegate_pubkey
        )

        blocks = get_blocks(
            cursor=cursor,
            max_timestamp=max_timestamp,
            pubkey=delegate_pubkey
        )

        if not last_payout:
            last_payout = get_last_payout(
                cursor=cursor,
                address=delegate_address
            )
        block_nr = 0

        for tx in transactions:
            if tx.timestamp >= blocks[block_nr].timestamp:
                cal_share(voters, last_payout, tx)
            else:
                parse(
                    tx=tx,
                    dict=voters,
                    address=delegate_address,
                    pubkey=delegate_pubkey
                      )

        return voters, max_timestamp

