from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from pub_sub import *
import unittest
import settings


class TestEndToEnd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        admin_cfg = copy.copy(settings.KAFKA_CONFIG)
        del admin_cfg['topics']
        cls.admin_client = KafkaAdminClient(**admin_cfg)
        try:
            cls.admin_client.delete_topics([settings.KAFKA_TOPIC], 10000)
        except Exception as e:
            log.exception(e)
            pass
        t = NewTopic(str(settings.KAFKA_TOPIC), 1, 3)
        cls.admin_client.create_topics([t], 100000)

    def test_end_to_end(self):
        publisher = MetricPublisher(settings.KAFKA_CONFIG)
        subscriber = MetricSubscriber(
            pull_config=settings.KAFKA_CONFIG,
            push_config={'connection_string': settings.POSTGRES_URI}
        )
        for _ in range(5):
            publisher.publish_one()
        publisher.publisher.flush(10000)
        payload = publisher.payload
        subscriber.produce_data()
        self.assertEqual(payload, subscriber.data)
        subscriber._save()
