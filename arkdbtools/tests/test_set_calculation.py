from unittest import TestCase


class TestSet_calculation(TestCase):

    def tearDown(self):
        from arkdbtools import config as c
        c.CALCULATION_SETTINGS['BLACKLIST'] = None
        c.CALCULATION_SETTINGS['EXCEPTIONS'] = None
        c.CALCULATION_SETTINGS['MAX'] = None
        c.CALCULATION_SETTINGS['SHARE_FEES'] = None

    def test_set_calculation(self):
        from arkdbtools import config as c
        from arkdbtools.dbtools import set_calculation

        resultset = {
            'BLACKLIST': '1',
            'EXCEPTIONS': '2',
            'MAX': '3',
            'SHARE_FEES': '4',
        }
        set_calculation(
            blacklist=  '1',
            exceptions= '2',
            max_amount=        '3',
            share_fees= '4',)
        self.assertCountEqual(c.CALCULATION_SETTINGS, resultset)

    def test_set_calculation_clear(self):
        from arkdbtools import config as c
        from arkdbtools.dbtools import set_calculation
        resultset = {
            'BLACKLIST': None,
            'EXCEPTIONS': None,
            'MAX': float('inf'),
            'SHARE_FEES': False,
        }
        c.CALCULATION_SETTINGS['BLACKLIST'] = '1'
        c.CALCULATION_SETTINGS['EXCEPTIONS'] = '2'
        c.CALCULATION_SETTINGS['MAX'] = '3'
        c.CALCULATION_SETTINGS['SHARE_FEES'] = '4'

        set_calculation()

        self.assertCountEqual(c.CALCULATION_SETTINGS, resultset)
