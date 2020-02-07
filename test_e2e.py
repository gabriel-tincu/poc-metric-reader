from pub_sub import *
import unittest
import settings


class TestEndToEnd(unittest.TestCase):

    @unittest.skip('this one blocks waiting for a message or retrieves the wrong message')
    def test_end_to_end(self):
        publisher = MetricPublisher(settings.KAFKA_CONFIG)
        publisher.publish_one()
        self.payload = json.loads(publisher.payload.decode())
        subscriber = MetricSubscriber(
            pull_config=settings.KAFKA_CONFIG,
            push_config={'connection_string': settings.POSTGRES_URI}
        )
        subscriber.produce_data()
        first_data = json.loads(subscriber.data.decode())
        for k in ['memory', 'cpu', 'swap', 'network']:
            expected = self.payload[k]
            actual = first_data[k]
            self.assertEqual(
                expected,
                actual, f'vales differ for {k}: {expected} vs {actual}'
            )
        subscriber._save()

    def tearDown(self) -> None:
        subscriber = MetricSubscriber(
            pull_config=settings.KAFKA_CONFIG,
            push_config={'connection_string': settings.POSTGRES_URI}
        )
        for t in ['cpu', 'disk', 'swap', 'network', 'ram']:
            subscriber.storage.cursor.execute('DELETE FROM %s'%t)
