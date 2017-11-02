from unittest import TestCase


class TestCore(TestCase):
    def setUp(self):
        from arkdbtools.dbtools import set_connection
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )

    def tearDown(self):
        from arkdbtools.dbtools import set_sender
        set_sender()

    def test_send(self):
        # feel free to write a unit test relying on a testnet wallet
        self.fail()

    def test_payoutsender(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        test_dict = {'address': {
            'share': 100 * ARK,
            'vote_timestamp': 10,
            'last_payout': 100,
            'status': True
        }}
        data = 'address', test_dict['address']

        set_sender(
            default_share= 0.7,
            cover_fees=False,
            share_percentage_exceptions=None,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )

        result, delegate_share, amount = Core.payoutsender(data)
        self.assertTrue(result)
        self.assertEqual(amount, 70*ARK)
        self.assertEqual(delegate_share, 30*ARK)

        set_sender(
            default_share=0.7,
            cover_fees=True,
            share_percentage_exceptions=None,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount = 70*ARK
        test_result_delegate_share = 30*ARK - TX_FEE
        result, delegate_share, amount = Core.payoutsender(data)
        self.assertTrue(result)
        self.assertEqual(amount, test_result_amount)
        self.assertEqual(delegate_share, test_result_delegate_share)

