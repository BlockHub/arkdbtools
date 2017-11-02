from unittest import TestCase


class TestSet_connection(TestCase):

    def tearDown(self):
        from arkdbtools import config as c
        c.CONNECTION['HOST'] = None
        c.CONNECTION['DATABASE'] = None
        c.CONNECTION['USER'] = None
        c.CONNECTION['PASSWORD'] = None

    def test_set_connection(self):
        from arkdbtools import config as c
        from arkdbtools.dbtools import set_connection

        resultset = {
            'HOST'    : '1',
            'DATABASE': '2',
            'USER'    : '3',
            'PASSWORD': '4',
        }

        set_connection(
            host='1',
            database='2',
            user='3',
            password='4'
        )
        self.assertCountEqual(c.CONNECTION, resultset)

    def test_set_connection_clear(self):
        from arkdbtools import config as c
        from arkdbtools.dbtools import set_connection

        resultset = {
            'HOST': None,
            'DATABASE': None,
            'USER': None,
            'PASSWORD': None,
        }
        c.CONNECTION['HOST'] = '1'
        c.CONNECTION['DATABASE'] = '2'
        c.CONNECTION['USER'] = '3'
        c.CONNECTION['PASSWORD'] = '4'

        set_connection()

        self.assertCountEqual(c.CONNECTION, resultset)