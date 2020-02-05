from pub_sub import *
import unittest
import os

PG_CONN_STR = os.getenv('PG_CONN_STR')


class TestEndToEnd(unittest.TestCase):
    def setUpClass(cls):
        cls.s = PostgresStorage() if not PG_CONN_STR else \
            PostgresStorage(PG_CONN_STR)
        cls.s.cursor.execute('CREATE TABLE ram (id ')
    def tearDownClass(cls):
        pass