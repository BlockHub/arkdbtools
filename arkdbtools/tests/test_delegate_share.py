from unittest import TestCase


class TestDelegateShare(TestCase):

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

    #todo make test_share a single module and test different combinations of settigs.
    def test_share(self):
        from arkdbtools.dbtools import Delegate, Address

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)
        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(timestamp, int)

        for i in payouts:
            self.assertIsInstance(i, str)
            self.assertIsInstance(payouts[i]['share'], float)
            self.assertIsInstance(payouts[i]['status'], bool)
            self.assertIsInstance(payouts[i]['vote_timestamp'], int)
            self.assertIsInstance(payouts[i]['last_payout'], int)

