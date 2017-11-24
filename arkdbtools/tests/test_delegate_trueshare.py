from unittest import TestCase


class TestDelegateTrueShare(TestCase):
    def setUp(self):
        from arkdbtools.dbtools import set_connection
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )

    def tearDown(self):
        from arkdbtools.dbtools import set_connection, set_calculation
        set_connection()
        set_calculation()

    def test_trueshare(self):
        from arkdbtools.dbtools import Delegate

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts, timestamp = Delegate.trueshare(del_pubkey=delegate_pubkey, del_address=delegate)
        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(timestamp, int)

        for i in payouts:
            self.assertIsInstance(i, str)
            self.assertIsInstance(payouts[i]['share'], float)
            self.assertIsInstance(payouts[i]['status'], bool)
            self.assertIsInstance(payouts[i]['vote_timestamp'], int)
            self.assertIsInstance(payouts[i]['last_payout'], int)

    def test_trueshare_settings_share_fees(self):
        from arkdbtools.dbtools import Delegate, set_calculation

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts_no_setting, timestamp = Delegate.trueshare(del_pubkey=delegate_pubkey, del_address=delegate)
        set_calculation(share_fees=True)
        payouts, timestamp = Delegate.trueshare(del_pubkey=delegate_pubkey, del_address=delegate)

        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        sum_payouts_no_settings = 0
        for i in payouts_no_setting:
            sum_payouts_no_settings += payouts_no_setting[i]['share']

        sum_payouts = 0
        for i in payouts:
            sum_payouts += payouts[i]['share']

        self.assertGreater(sum_payouts, sum_payouts_no_settings)

    def test_true_share_setting_blacklist(self):
        from arkdbtools.dbtools import Delegate, set_calculation

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts_no_setting, timestamp = Delegate.trueshare(del_pubkey=delegate_pubkey, del_address=delegate)

        set_calculation(
            blacklist=['AJwHyHAArNmzGfmDnsJenF857ATQevg8HY'],
        )
        payouts, timestamp = Delegate.trueshare(del_pubkey=delegate_pubkey, del_address=delegate)

        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        self.assertFalse(payouts == payouts_no_setting)
        self.assertTrue(len(payouts) < len(payouts_no_setting))