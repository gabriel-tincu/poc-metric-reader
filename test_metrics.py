import unittest
import metrics

class CollectorTest(unittest.TestCase):

    def test_result(self):
        # do i really need this??
        collector = metrics.MetricsCollector()
        p = next(collector.gather())
        self.assertIsNotNone(p)
        for k in ['memory', 'cpu', 'network', 'disk', 'swap']:
            self.assertIsNotNone(p[k])
        self.assertTrue(len(p['disk']['usage']) > 0)
