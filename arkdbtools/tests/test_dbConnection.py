from unittest import TestCase
import arkdbtools as at


class TestDbConnection(TestCase):
    def tearDown(self):
        at.CONNECTION['HOST']       = None
        at.CONNECTION['DATABASE']   = None
        at.CONNECTION['USER']       = None
        at.CONNECTION['PASSWORD']   = None

    def test_set_connection(self):
        at.set_connection(host="localhost",
                          database="ark_mainnet",
                          user="test",
                          password='test')
        self.assertCountEqual(at.CONNECTION, {"HOST": "localhost",
                                              "DATABASE": "ark_mainnet",
                                              "USER": "test",
                                              "PASSWORD": 'test'}
                              )


