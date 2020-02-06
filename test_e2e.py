from pub_sub import *
import unittest
import settings


class TestEndToEnd(unittest.TestCase):
    def setUpClass(cls):
        cls.s = PostgresStorage(settings.POSTGRES_URI)
        cls.s.cursor.execute('CREATE TABLE ram (id SERIAL PRIMARY KEY, '
                             'ctime TIMESTAMP DEFAULT LOCALTIME'
                             'total NUMERIC, available NUMERIC, used NUMERIC, '
                             'free NUMERIC, percent NUMERIC')
        cls.s.cursor.execute('CREATE TABLE cpu (id SERIAL PRIMARY KEY, '
                             'ctime TIMESTAMP DEFAULT LOCALTIME'
                             'percent NUMERIC, idle NUMERIC, system NUMERIC, '
                             'user NUMERIC')
        cls.s.cursor.execute('CREATE TABLE disk (id SERIAL PRIMARY KEY, '
                             'ctime TIMESTAMP DEFAULT LOCALTIME'
                             'device TEXT, mountpoint TEXT, total NUMERIC, '
                             'used NUMERIC, free NUMERIC, percent NUMERIC')
        cls.s.cursor.execute('CREATE TABLE swap (id SERIAL PRIMARY KEY, '
                             'ctime TIMESTAMP DEFAULT LOCALTIME'
                             'total NUMERIC, used NUMERIC, free NUMERIC, '
                             'percent NUMERIC')
        cls.s.cursor.execute('CREATE TABLE network (id SERIAL PRIMARY KEY, '
                             'ctime TIMESTAMP DEFAULT LOCALTIME'
                             'bytes_sent NUMERIC, bytes_recv NUMERIC')
        cls.s.conn.commit()

    def tearDownClass(cls):
        for t in ['ram', 'disk', 'cpu', 'network', 'swap']:
            cls.s.cursor.execute('DROP TABLE IF EXISTS %s CASCADE', t)
        cls.s.conn.commit()
