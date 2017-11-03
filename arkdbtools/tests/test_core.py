from unittest import TestCase


class TestCore(TestCase):
    def setUp(self):
        from arkdbtools.dbtools import set_connection, set_sender
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )
        set_sender()

    def tearDown(self):
        from arkdbtools.dbtools import set_sender
        set_sender()

    def test_payoutsender_default_share(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
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

    def test_payoutsender_settings_cover_fees(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {'address': {
            'share': 100 * ARK,
            'vote_timestamp': 10,
            'last_payout': 100,
            'status': True
        }}
        data = 'address', test_dict['address']
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
        test_result_amount = 70*ARK + TX_FEE
        test_result_delegate_share = 30*ARK - TX_FEE
        result, delegate_share, amount = Core.payoutsender(data)
        self.assertTrue(result)
        self.assertEqual(amount, test_result_amount)
        self.assertEqual(delegate_share, test_result_delegate_share)

    def test_payoutsender_settings_share_percentage_exceptions_no_cover_fees(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {'address': {
            'share': 100 * ARK,
            'vote_timestamp': 10,
            'last_payout': 100,
            'status': True
        }}

        exceptions = {'address': 0.8}
        data = 'address', test_dict['address']
        set_sender(
            default_share=0.7,
            cover_fees=False,
            share_percentage_exceptions=exceptions,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount = 80*ARK
        test_result_delegate_share = 20*ARK
        result, delegate_share, amount = Core.payoutsender(data)

        self.assertTrue(result)
        self.assertEqual(amount, test_result_amount)
        self.assertEqual(delegate_share, test_result_delegate_share)

    def test_payoutsender_settings_share_percentage_exceptions_cover_fees(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {'address': {
            'share': 100 * ARK,
            'vote_timestamp': 10,
            'last_payout': 100,
            'status': True
        }}

        exceptions = {'address': 0.8}
        data = 'address', test_dict['address']
        set_sender(
            default_share=0.7,
            cover_fees=True,
            share_percentage_exceptions=exceptions,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount = 80*ARK + TX_FEE
        test_result_delegate_share = 20*ARK - TX_FEE
        result, delegate_share, amount = Core.payoutsender(data)

        self.assertTrue(result)
        self.assertEqual(amount, test_result_amount)
        self.assertEqual(delegate_share, test_result_delegate_share)

    def test_payoutsender_settings_timestamp_brackets_cover_fees(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {
            'address1': {
                'share': 100 * ARK,
                'vote_timestamp': 10,
                'last_payout': 100,
                'status': True},
            'address2': {
                'share': 100 * ARK,
                'vote_timestamp': 90,
                'last_payout': 100,
                'status': True}
            }


        timestamp_brackets = {
            float('inf'): 0.8,
            20: 0.9
        }
        data1 = 'address1', test_dict['address1']
        data2 = 'address2', test_dict['address2']
        set_sender(
            default_share=0.7,
            cover_fees=True,
            share_percentage_exceptions=None,
            timestamp_brackets=timestamp_brackets,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount1 = 90*ARK + TX_FEE
        test_result_delegate_share1 = 10*ARK - TX_FEE

        test_result_amount2 = 80 * ARK + TX_FEE
        test_result_delegate_share2 = 20 * ARK - TX_FEE

        result1, delegate_share1, amount1 = Core.payoutsender(data1)
        result2, delegate_share2, amount2 = Core.payoutsender(data2)

        self.assertTrue(result1)
        self.assertTrue(result2)

        self.assertEqual(amount1, test_result_amount1)
        self.assertEqual(delegate_share1, test_result_delegate_share1)

        self.assertEqual(amount2, test_result_amount2)
        self.assertEqual(delegate_share2, test_result_delegate_share2)

    def test_payoutsender_settings_timestamp_brackets_no_cover_fees(self):
        from arkdbtools.dbtools import set_sender, Core
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {
            'address1': {
                'share': 100 * ARK,
                'vote_timestamp': 10,
                'last_payout': 100,
                'status': True},
            'address2': {
                'share': 100 * ARK,
                'vote_timestamp': 90,
                'last_payout': 100,
                'status': True}
        }

        timestamp_brackets = {
            float('inf'): 0.8,
            20: 0.9
        }
        data1 = 'address1', test_dict['address1']
        data2 = 'address2', test_dict['address2']
        set_sender(
            default_share=0.7,
            cover_fees=False,
            share_percentage_exceptions=None,
            timestamp_brackets=timestamp_brackets,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=14,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount1 = 90 * ARK
        test_result_delegate_share1 = 10 * ARK

        test_result_amount2 = 80 * ARK
        test_result_delegate_share2 = 20 * ARK

        result1, delegate_share1, amount1 = Core.payoutsender(data1)
        result2, delegate_share2, amount2 = Core.payoutsender(data2)

        self.assertTrue(result1)
        self.assertTrue(result2)

        self.assertEqual(amount1, test_result_amount1)
        self.assertEqual(delegate_share1, test_result_delegate_share1)

        self.assertEqual(amount2, test_result_amount2)
        self.assertEqual(delegate_share2, test_result_delegate_share2)

    def test_payoutsender_settings_min_payout_weekly(self):
        from arkdbtools.dbtools import set_sender, Core, TxParameterError
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {
            # has min amount, so should pass
            'address1': {
                'share': 10000 * ARK,
                'vote_timestamp': 10,
                'last_payout': 10,
                'status': True},
            # does not have the min amount, but last_payout is early enough
            'address2': {
                'share': 50 * ARK,
                'vote_timestamp': 90,
                'last_payout': 100,
                'status': True},
            # share > than min, but last payout not recent enough
            'address3': {
                'share': 10000 * ARK,
                'vote_timestamp': 90,
                'last_payout': float('inf'),
                'status': True}
        }

        frq_dict = {
             'address1': 2,
             'address2': 2,
             'address3': 2,
        }

        data1 = 'address1', test_dict['address1']
        data2 = 'address2', test_dict['address2']
        data3 = 'address3', test_dict['address3']

        set_sender(
            default_share=0.7,
            cover_fees=False,
            share_percentage_exceptions=None,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=90*ARK,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=datetime.today().month,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount1 = 7000 * ARK
        test_result_delegate_share1 = 3000 * ARK


        result1, delegate_share1, amount1 = Core.payoutsender(data1, frq_dict=frq_dict)

        self.assertTrue(result1)
        self.assertTrue(test_result_amount1 == amount1)
        self.assertTrue(test_result_delegate_share1, delegate_share1)

        self.assertRaises(TxParameterError, Core.payoutsender, data=data2, frq_dict=frq_dict)
        self.assertRaises(TxParameterError, Core.payoutsender, data=data3, frq_dict=frq_dict)

    def test_payoutsender_settings_min_payout_monthly(self):
        from arkdbtools.dbtools import set_sender, Core, TxParameterError
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {
            # has min amount, so should pass
            'address1': {
                'share': 10000 * ARK,
                'vote_timestamp': 10,
                'last_payout': 10,
                'status': True},
            # does not have the min amount, but last_payout is early enough
            'address2': {
                'share': 50 * ARK,
                'vote_timestamp': 90,
                'last_payout': 100,
                'status': True},
            # share > than min, but last payout not recent enough
            'address3': {
                'share': 10000 * ARK,
                'vote_timestamp': 90,
                'last_payout': float('inf'),
                'status': True}
        }

        frq_dict = {
            'address1': 3,
            'address2': 3,
            'address3': 3,
        }

        data1 = 'address1', test_dict['address1']
        data2 = 'address2', test_dict['address2']
        data3 = 'address3', test_dict['address3']

        set_sender(
            default_share=0.7,
            cover_fees=False,
            share_percentage_exceptions=None,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=90*ARK,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=datetime.today().month,
            payoutsender_test=True,
            sender_exception=None
        )
        test_result_amount1 = 7000 * ARK
        test_result_delegate_share1 = 3000 * ARK

        result1, delegate_share1, amount1 = Core.payoutsender(data1, frq_dict=frq_dict)

        self.assertTrue(result1)
        self.assertTrue(test_result_amount1 == amount1)
        self.assertTrue(test_result_delegate_share1, delegate_share1)

        self.assertRaises(TxParameterError, Core.payoutsender, data=data2, frq_dict=frq_dict)
        self.assertRaises(TxParameterError, Core.payoutsender, data=data3, frq_dict=frq_dict)

    def test_payoutsender_settings_sender_exceptions(self):
        from arkdbtools.dbtools import set_sender, Core, AllocationError
        from arkdbtools.config import TX_FEE, ARK
        from datetime import datetime
        set_sender()
        test_dict = {
            # has min amount, so should pass
            'address1': {
                'share': 10000 * ARK,
                'vote_timestamp': 10,
                'last_payout': 10,
                'status': True},
            'address2': {
                'share': 50 * ARK,
                'vote_timestamp': 90,
                'last_payout': 100,
                'status': True},
            'address3': {
                'share': 50 * ARK,
                'vote_timestamp': 90,
                'last_payout': float('inf'),
                'status': True}
        }

        sender_exceptions = {
            #has an illegal frequency, so should raise AllocationError
            'address1': {
                'AMOUNT': 45 * ARK,
                'FREQUENCY': 4
            },
            # amount < share, so should pass
            'address2' : {
                'AMOUNT': 45 * ARK,
                'FREQUENCY': 1
            },
            # amount > share, so should raise AllocationError
            'address3': {
                'AMOUNT': 4500 * ARK,
                'FREQUENCY': 1}
        }


        data1 = 'address1', test_dict['address1']
        data2 = 'address2', test_dict['address2']
        data3 = 'address3', test_dict['address3']

        set_sender(
            default_share=0.7,
            cover_fees=False,
            share_percentage_exceptions=None,
            timestamp_brackets=None,
            min_payout_daily=0,
            min_payout_weekly=0,
            min_payout_monthly=0,
            day_weekly_payout=datetime.today().weekday(),
            day_monthly_payout=datetime.today().month,
            payoutsender_test=True,
            sender_exception=sender_exceptions
        )

        self.assertRaises(AllocationError, Core.payoutsender, data1)
        self.assertRaises(AllocationError, Core.payoutsender, data3)

        test_delegate_share = 5*ARK
        test_amount = 45 * ARK

        result, delageteshare, amount = Core.payoutsender(data2)
        self.assertTrue(result)
        self.assertEquals(delageteshare, test_delegate_share)
        self.assertEquals(amount, test_amount)
