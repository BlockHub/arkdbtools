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
        from arkdbtools.dbtools import set_connection, set_calculation
        set_connection()
        set_calculation()

    def test_share_no_settings(self):
        from arkdbtools.dbtools import Delegate

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

    def test_share_setting_blacklist(self):
        from arkdbtools.dbtools import Delegate, set_calculation

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts_no_setting, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        set_calculation(
            blacklist=['AJwHyHAArNmzGfmDnsJenF857ATQevg8HY'],
                        )
        payouts, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        self.assertFalse(payouts == payouts_no_setting)
        self.assertTrue(len(payouts) < len(payouts_no_setting))

    def test_share_setting_exception(self):
        from arkdbtools.dbtools import Delegate, set_calculation
        from arkdbtools.config import ARK

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        address = 'AJwHyHAArNmzGfmDnsJenF857ATQevg8HY'
        payouts_no_setting, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        exception = {address: {'REPLACE': 100000*ARK}}
        exception2 = {address: {'REPLACE': 0}}
        set_calculation(
            exceptions=exception,
                        )
        payouts, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        set_calculation(
            exceptions=exception2,
        )


        payouts2, timestamp2 = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)


        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        self.assertTrue(payouts.items() <= payouts_no_setting.items())

        # the address has a very low balance, so 100000 ARK shouldn't overide its share value,
        # since it is too low
        self.assertTrue(payouts_no_setting[address]['share'] == payouts[address]['share'])

        # now we have replaced its value by 0, so the share should be 0
        self.assertTrue(payouts_no_setting[address]['share'] > payouts2[address]['share'])


    def test_share_settings_max(self):
        from arkdbtools.dbtools import Delegate, set_calculation
        from arkdbtools.config import ARK

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts_no_setting, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)
        set_calculation(max_amount=0.0000001)
        payouts, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        previous_key = list(payouts.keys())[0]

        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        for i in list(payouts.keys())[:1]:
            if payouts[i]['share'] != 0 and payouts[i]['balance'] > 0.0000001:
                self.assertAlmostEquals(payouts[i]['share'], payouts[previous_key]['share'], 10)
                previous_key = i

    def test_share_settings_share_fees(self):
        from arkdbtools.dbtools import Delegate, set_calculation

        delegate = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        delegate_pubkey = '0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a'

        payouts_no_setting, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)
        set_calculation(share_fees=True)
        payouts, timestamp = Delegate.share(del_pubkey=delegate_pubkey, del_address=delegate)

        self.assertIsInstance(payouts, dict)
        self.assertIsInstance(payouts_no_setting, dict)

        sum_payouts_no_settings = 0
        for i in payouts_no_setting:
            sum_payouts_no_settings += payouts_no_setting[i]['share']

        sum_payouts = 0
        for i in payouts:
            sum_payouts += payouts[i]['share']

        self.assertGreater(sum_payouts, sum_payouts_no_settings)