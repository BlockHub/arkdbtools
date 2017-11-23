from unittest import TestCase


class TestDelegate(TestCase):

    def setUp(self):
        from arkdbtools.dbtools import set_connection
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )

    def tearDown(self):
        from arkdbtools.dbtools import set_connection
        set_connection()

    def test_delegates(self):
        from arkdbtools.dbtools import Delegate
        delegates = Delegate.delegates()
        self.assertIsInstance(delegates, list)
        for i in delegates:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.username, str)
            self.assertIsInstance(i.pubkey, str)
            self.assertIsInstance(i.timestamp, int)
            self.assertIsInstance(i.address, str)
            self.assertIsInstance(i.transactionId, str)

    def test_lastpayout(self):
        from arkdbtools.dbtools import Delegate

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        blacklist_address_single = ['AJwHyHAArNmzGfmDnsJenF857ATQevg8HY']
        blacklist_address_double = ['AJwHyHAArNmzGfmDnsJenF857ATQevg8HY', 'AedhaXxsJap6GopDFhtT1PmaqWTbGMwWcE']
        blacklist_transaction_single = ['e44a01244b0d67ab8e5814065361a1d488831a50c5a8c85164005f0496c78d94']
        blacklist_transaction_double = ['e44a01244b0d67ab8e5814065361a1d488831a50c5a8c85164005f0496c78d94', 'bd99bf2d6e8f0113a8fccf2d35b2347c0cbac0528f8cd295ebf56567c2aad81a']

        last_payout = Delegate.lastpayout(delegate)
        last_payout_blacklist_address_single = Delegate.lastpayout(delegate, blacklist_address_single)
        last_payout_blacklist_transaction_single = Delegate.lastpayout(delegate, blacklist_transaction_single)
        last_payout_blacklist_address_double = Delegate.lastpayout(delegate, blacklist_address_double)
        last_payout_blacklist_transaction_double = Delegate.lastpayout(delegate, blacklist_transaction_double)

        for i in [last_payout, last_payout_blacklist_address_single, last_payout_blacklist_address_double,
                  last_payout_blacklist_transaction_single, last_payout_blacklist_transaction_double]:
            self.assertIsInstance(i, list)
            self.assertTrue(i)
            for x in i:
                self.assertIsInstance(x, tuple)
                self.assertIsInstance(x.address, str)
                self.assertIsInstance(x.id, str)
                self.assertIsInstance(x.timestamp, int)

        self.assertTrue(
            len(last_payout)-len(last_payout_blacklist_transaction_single) == 0
        )
        self.assertTrue(
            len(last_payout) - len(last_payout_blacklist_address_single) == 1
        )
        self.assertTrue(
            len(last_payout) - len(last_payout_blacklist_transaction_double) == 0
        )
        self.assertTrue(
            len(last_payout) - len(last_payout_blacklist_address_double) == 2
        )

        self.assertTrue(
            len(last_payout_blacklist_transaction_single) - len(last_payout_blacklist_address_single) == 1
        )
        self.assertTrue(
            len(last_payout_blacklist_transaction_double) - len(last_payout_blacklist_address_double) == 2
        )
        self.assertNotEqual(sorted(last_payout), sorted(last_payout_blacklist_transaction_single))
        self.assertNotEqual(sorted(last_payout), sorted(last_payout_blacklist_transaction_double))

        # this test also depends on the state of the DB used
        # self.assertNotEqual(sorted(last_payout_blacklist_transaction_single), sorted(last_payout_blacklist_transaction_double))


    def test_votes(self):
        from arkdbtools.dbtools import Delegate

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        votes = Delegate.votes(delegate)
        self.assertIsInstance(votes, list)
        for i in votes:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.address, str)
            self.assertIsInstance(i.timestamp, int)


    def test_unvotes(self):
        from arkdbtools.dbtools import Delegate

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        unvotes = Delegate.unvotes(delegate)
        self.assertIsInstance(unvotes, list)
        for i in unvotes:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.address, str)
            self.assertIsInstance(i.timestamp, int)

    def test_voters(self):
        from arkdbtools.dbtools import Delegate

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        voters = Delegate.voters(delegate)
        unvotes = Delegate.unvotes(delegate)
        votes = Delegate.votes(delegate)

        self.assertIsInstance(voters, list)
        self.assertGreaterEqual(votes, voters)
        self.assertGreaterEqual(voters, unvotes)

        for i in voters:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.address, str)
            self.assertIsInstance(i.timestamp, int)

    def test_blocks(self):
        from arkdbtools.dbtools import Delegate
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'
        max_timestamp = 19000000
        blocks = Delegate.blocks(delegate_pubkey)
        blocks_max_timestamp = Delegate.blocks(delegate_pubkey, max_timestamp)

        for i in [blocks, blocks_max_timestamp]:
            self.assertIsInstance(i, list)
            for x in i:
                self.assertIsInstance(x, tuple)
                self.assertIsInstance(x.timestamp, int)
                self.assertIsInstance(x.height, int)
                self.assertIsInstance(x.id, str)
                self.assertIsInstance(x.totalFee, int)
                self.assertIsInstance(x.reward, int)
        self.assertGreaterEqual(blocks, blocks_max_timestamp)
