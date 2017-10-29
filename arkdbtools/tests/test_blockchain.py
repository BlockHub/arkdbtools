from unittest import TestCase
from unittest.mock import Mock, patch


class TestBlockchain(TestCase):
    # rather lazy test, but it does the trick for our purposes
    def test_height(self):
        import arkdbtools as at

        # use a single function call to speed up test
        res = at.Blockchain.height()
        self.assertIsInstance(res, int)
        self.assertGreater(res, 2379409)
