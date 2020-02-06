from pub_sub import *
import unittest
import settings


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.publisher = MetricPublisher()
