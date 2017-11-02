from unittest import TestCase


class TestSet_delegate(TestCase):

    def tearDown(self):
        from arkdbtools import config as c
        c.DELEGATE['ADDRESS'] = None
        c.DELEGATE['PUBKEY'] = None
        c.DELEGATE['SECRET'] = None

    def test_set_delegate(self):
        from arkdbtools.dbtools import set_delegate
        from arkdbtools import config as c

        resultset = {
            'ADDRESS': '1',
            'PUBKEY':  '2',
            'SECRET':  '3'}

        set_delegate(
            address= '1',
            pubkey=  '2',
            secret=  '3')
        self.assertCountEqual(c.DELEGATE, resultset)