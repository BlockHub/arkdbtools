from unittest import TestCase


class TestSet_sender(TestCase):

    def tearDown(self):
        from arkdbtools import config as c

        c.SENDER_SETTINGS['DEFAULT_SHARE'] = None
        c.SENDER_SETTINGS['COVER_FEES'] = None
        c.SENDER_SETTINGS['SHARE_PERCENTAGE_EXCEPTIONS'] = None
        c.SENDER_SETTINGS['TIMESTAMP_BRACKETS'] = None
        c.SENDER_SETTINGS['MIN_PAYOUT_DAILY'] = None
        c.SENDER_SETTINGS['MIN_PAYOUT_WEEKLY'] = None
        c.SENDER_SETTINGS['MIN_PAYOUT_MONTHLY'] = None
        c.SENDER_SETTINGS['DAY_WEEKLY_PAYOUT'] = None
        c.SENDER_SETTINGS['DAY_MONTHLY_PAYOUT'] = None
        c.SENDER_SETTINGS['PAYOUTSENDER_TEST'] = None
        c.SENDER_SETTINGS['SENDER_EXCEPTION'] = None

    def test_set_sender(self):
        from arkdbtools import config as c
        from arkdbtools.dbtools import set_sender

        resultset = {
            'DEFAULT_SHARE': '1',
            'COVER_FEES': '2',
            'SHARE_PERCENTAGE_EXCEPTIONS': '3',
            'TIMESTAMP_BRACKETS': '4',
            'MIN_PAYOUT_DAILY': '5',
            'MIN_PAYOUT_WEEKLY': '6',
            'MIN_PAYOUT_MONTHLY': '7',
            'DAY_WEEKLY_PAYOUT': '8',
            'DAY_MONTHLY_PAYOUT': '9',
            'PAYOUTSENDER_TEST': '10',
            'SENDER_EXCEPTION': '11'
        }

        set_sender(
            default_share='1',
            cover_fees='2',
            share_percentage_exceptions='3',
            timestamp_brackets='4',
            min_payout_daily='5',
            min_payout_weekly='6',
            min_payout_monthly='7',
            day_weekly_payout='8',
            day_monthly_payout='9',
            payoutsender_test='10',
            sender_exception='11'
                   )
        self.assertCountEqual(c.SENDER_SETTINGS, resultset)
