from unittest import TestCase


class TestGet_transactionlist(TestCase):

    def setUp(self):
        from arkdbtools.dbtools import set_connection
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )

    def test_get_transactionlist(self):
        from arkdbtools.dbtools import get_transactionlist


        delegate_pubkey = 'AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE'
        transactionlist = get_transactionlist(delegate_pubkey)

        self.assertIsInstance(transactionlist, list)
        self.assertTrue(list)

        for i in transactionlist:
            self.assertIsInstance(i, tuple)
            self.assertIsInstance(i.id, str)
            self.assertIsInstance(i.amount, int)
            self.assertIsInstance(i.recipientId, str)
            self.assertIsInstance(i.senderId, str)
            self.assertIsInstance(i.rawasset, str)
            self.assertIsInstance(i.type, int)
            self.assertIsInstance(i.fee, int)