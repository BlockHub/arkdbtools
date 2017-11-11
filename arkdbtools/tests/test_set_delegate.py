from unittest import TestCase


class TestSet_delegate(TestCase):

    def tearDown(self):
        from arkdbtools import config as c
        c.DELEGATE['ADDRESS'] = None
        c.DELEGATE['PUBKEY'] = None
        c.DELEGATE['PASSPHRASE'] = None

    def test_set_delegate(self):
        from arkdbtools.dbtools import set_delegate
        from arkdbtools import config as c

        resultset = {
            'ADDRESS': '1',
            'PUBKEY':  '2',
            'PASSPHRASE':  '3'}

        set_delegate(
            address= '1',
            pubkey=  '2',
            secret=  '3',
        )
        self.assertCountEqual(c.DELEGATE, resultset)

    def test_set_delegate_clear(self):
        from arkdbtools.dbtools import set_delegate
        from arkdbtools import config as c

        resultset = {
            'ADDRESS': None,
            'PUBKEY': None,
            'PASSPHRASE': None,
        }

        c.DELEGATE['ADDRESS'] = '1'
        c.DELEGATE['PUBKEY'] = '2'
        c.DELEGATE['PASSPHRASE'] = '3'

        set_delegate()

        self.assertCountEqual(c.DELEGATE, resultset)