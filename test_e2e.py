from pub_sub import *
import unittest
import settings
import decimal
import json
from test_integration import clean_db, get_from_storage
from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.cluster import TopicPartition


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        clean_db()
        cfg = copy.copy(settings.KAFKA_CONFIG)
        del cfg['topics']
        del cfg['consumer_timeout_ms']

        self.admin = KafkaAdminClient(**cfg)
        try:
            self.admin.create_topics(
                [NewTopic(settings.KAFKA_TOPIC, 1, 1)],
                timeout_ms=5000
            )
        except:
            pass
        self.publisher = MetricPublisher(settings.KAFKA_CONFIG)
        self.subscriber = MetricSubscriber(
            pull_config=settings.KAFKA_CONFIG,
            push_config={'connection_string': settings.POSTGRES_URI}
        )

    def test_end_to_end(self):
        self.publisher.publish_one()
        self.subscriber.provider.seek(
            TopicPartition(settings.KAFKA_TOPIC, 0), 0
        )
        self.payload = json.loads(self.publisher.payload.decode())
        self.subscriber.consume_one()
        first_data = self.subscriber.data
        for k in ['memory', 'cpu', 'swap', 'network']:
            expected = self.payload[k]
            actual = first_data[k]
            for sub_k in expected.keys():
                sub_ex = expected[sub_k]
                sub_ac = actual[sub_k]
                self.assertEqual(
                    sub_ex,
                    sub_ac, f'vales differ for {k} on {sub_k}: {sub_ex} vs {sub_ac}'
                )
        res = get_from_storage()
        for key in ['memory', 'cpu', 'network']:
            for sub_key in first_data[key]:
                sent = first_data[key][sub_key]
                retrieved = res[key][sub_key]
                if type(retrieved) == decimal.Decimal:
                    retrieved = float(retrieved)
                err_msg = f'Values differ for {key} on {sub_key}'
                self.assertAlmostEqual(sent, retrieved, 2, err_msg)

    def tearDown(self) -> None:
        self.admin.delete_topics([settings.KAFKA_TOPIC])
        clean_db()
