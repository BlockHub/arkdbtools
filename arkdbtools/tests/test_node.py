from unittest import TestCase
"""These are not real unit tests, as they rely on the database to be correct, 
and the DbCursor class to be correct as well """


class TestNode(TestCase):
    def setUp(self):
        from arkdbtools.dbtools import set_connection
        set_connection(
            host='localhost',
            database='ark_mainnet',
            user='ark'
        )

    def tearDown(self):
        from arkdbtools.dbtools import set_connection
        set_connection()

    def test_height(self):
        from arkdbtools.dbtools import Node

        height = Node.height()
        self.assertIsInstance(height, int)

    def test_check_node(self):
        from arkdbtools.dbtools import Node

        # This test could potentially return a true, as Blockchain.height() is queried before Node.height()
        bool_false = Node.check_node(0)
        bool_true = Node.check_node(float('inf'))
        self.assertIsInstance(bool_false, bool)
        self.assertFalse(bool_false)
        self.assertIsInstance(bool_true, bool)
        self.assertTrue(bool_true)

    def test_max_timestamp(self):
        from arkdbtools.dbtools import Node

        max_timestamp = Node.max_timestamp()
        self.assertIsInstance(max_timestamp, int)

