from unittest import TestCase
"""This is not a real unit test, as it relies on the api to be properly working"""


class TestBlockchain(TestCase):
    def test_height(self):
        from arkdbtools.dbtools import Blockchain
        height = Blockchain.height()
        self.assertIsInstance(height, int)