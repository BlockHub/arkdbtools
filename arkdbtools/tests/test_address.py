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
