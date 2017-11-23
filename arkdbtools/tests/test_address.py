from unittest import TestCase


class TestAddress(TestCase):
    def setUp(self):
        from arkdbtools.dbtools import set_connection
        from arky import api
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )
        api.use('ark')

    def tearDown(self):
        from arkdbtools.dbtools import set_connection
        set_connection()

    def test_transactions(self):
        from arkdbtools.dbtools import Address
        transactions = Address.transactions('AMbR3sWGzF3rVqBrgYRnAvxL2TVh44ZEft')
        self.assertIsInstance(transactions, list)
        for i in transactions:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.id, str)
            self.assertIsInstance(i.amount, int)
            self.assertIsInstance(i.timestamp, int)
            self.assertIsInstance(i.recipientId, str)
            self.assertIsInstance(i.senderId, str)
            self.assertIsInstance(i.rawasset, str)
            self.assertIsInstance(i.type, int)
            self.assertIsInstance(i.fee, int)

    def test_votes(self):
        from arkdbtools.dbtools import Address
        votes = Address.votes('AMbR3sWGzF3rVqBrgYRnAvxL2TVh44ZEft')
        self.assertIsInstance(votes, list)
        for i in votes:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.direction, bool)
            self.assertIsInstance(i.delegate, str)
            self.assertIsInstance(i.timestamp, int)

    def test_balance(self):
        from arkdbtools.dbtools import Address
        from arkdbtools.utils import api_call
        from arky import api
        balance = Address.balance('AXx4bD2qrL1bdJuSjePawgJxQn825aNZZC')
        apibalance = int(api_call(api.Account.getBalance, 'AXx4bD2qrL1bdJuSjePawgJxQn825aNZZC')['balance'])

        self.assertIsInstance(balance, int)
        self.assertIsInstance(apibalance, int)
        self.assertEquals(balance, apibalance)

    def test_payout(self):
        from arkdbtools.dbtools import Address
        address = 'AMbR3sWGzF3rVqBrgYRnAvxL2TVh44ZEft'
        payouts = Address.payout(address)

        self.assertIsInstance(payouts, list)

        # this test depends on the state of Ark, in my testnode, only 2 payouts have occured
        # (it is not connected to the network and thus does not update
        # self.assertTrue(len(payouts) == 2)

        for i in payouts:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.id, str)
            self.assertIsInstance(i.amount, int)
            self.assertIsInstance(i.timestamp, int)
            self.assertIsInstance(i.recipientId, str)
            self.assertIsInstance(i.senderId, str)
            self.assertIsInstance(i.rawasset, str)
            self.assertIsInstance(i.type, int)
            self.assertIsInstance(i.fee, int)

    def test_balance_over_time(self):
        from arkdbtools.dbtools import Address

        # for a normal address
        address = 'AMbR3sWGzF3rVqBrgYRnAvxL2TVh44ZEft'
        balance = Address.balance(address)
        balance_over_time = Address.balance_over_time(address)

        self.assertIsInstance(balance_over_time, list)
        for i in balance_over_time:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.timestamp, int)
            self.assertIsInstance(i.amount, int)

        self.assertEqual(balance, balance_over_time[len(balance_over_time)-1].amount)

        # now for a delegate
        address = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        balance = Address.balance(address)
        balance_over_time = Address.balance_over_time(address)

        self.assertIsInstance(balance_over_time, list)
        for i in balance_over_time:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.timestamp, int)
            self.assertIsInstance(i.amount, int)

        self.assertEqual(balance, balance_over_time[-1].amount)

