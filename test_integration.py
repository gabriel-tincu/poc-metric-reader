from pub_sub import *
import unittest
import settings
import metrics
import json
import copy
import decimal
from collections import namedtuple
mock_type = namedtuple('KafkaMessage', ['key', 'provider', 'topic', 'value'])

mock_message = json.dumps({
    'data': 'mock'
}).encode()


class MockFuture:
    def __init__(self, data):
        self.data = data

    def get(self,*args, **kwargs):
        return self.data


class MockPublisher:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def send(topic, data, *args, **kwargs):
        return MockFuture(data)


class MockSubscriber:
    def __init__(self, *args, **kwargs):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        return mock_type('key', 'prov', 'metrics', mock_message)

    def assignment(self):
        return ['metrics']

    def poll(self, duration, *args, **kwargs):
        return [mock_type('key', 'prov', 'metrics', mock_message)]

    def assign(self, *args, **kwargs):
        pass

    def topics(self):
        return {'test'}


class MockStorage:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def save(data):
        return data


subscriber = MetricSubscriber(
    pull_config=copy.copy(settings.KAFKA_CONFIG),
    push_config={'connection_string': settings.POSTGRES_URI},
    pull_class=MockSubscriber,
    storage_class=PostgresStorage
)


class TestPublisher(unittest.TestCase):
    # i am seriously out of ideas...
    def setUp(self):
        self.publisher = MetricPublisher(
            copy.copy(settings.KAFKA_CONFIG),
            publisher_class=MockPublisher
        )

    def test_one_publish(self):
        res = self.publisher.publish_one()
        self.assertIsNotNone(res)
        sent = json.loads(res.get().decode())
        for k in ['memory', 'network', 'disk', 'swap', 'cpu']:
            self.assertTrue(k in sent)


class TestSubscriber(unittest.TestCase):
    def setUp(self):
        self.subscriber = MetricSubscriber(
            pull_config=copy.copy(settings.KAFKA_CONFIG),
            push_config={},
            pull_class=MockSubscriber,
            storage_class=MockStorage
        )

    def test_one_persist(self):
        self.subscriber.consume_one()
        data = self.subscriber.raw_data
        self.assertIsNotNone(data)

    def test_decoding_succeeds(self):
        self.subscriber.raw_data = mock_message
        self.subscriber._decode()
        self.assertIsNotNone(self.subscriber.data)
        self.assertEqual(self.subscriber.data['data'], 'mock', 'malformed decoded package')

    def test_decoding_fails(self):
        self.subscriber.raw_data = b'not json'
        self.assertRaises(MessageDecodeException, self.subscriber._decode)


def clean_db():
    for t in ['cpu', 'disk', 'swap', 'network', 'ram']:
        subscriber.storage.cursor.execute('DELETE FROM %s' % t)
    subscriber.storage.conn.commit()


def build_dict(cursor, row):
    x = {}
    for key, col in enumerate(cursor.description):
        x[col[0]] = row[key]
    return x


def get_from_storage():
    subscriber.storage.cursor.execute(
        'SELECT * FROM network ORDER BY ID DESC LIMIT 1'
    )
    network = build_dict(subscriber.storage.cursor,
                         subscriber.storage.cursor.fetchone())
    subscriber.storage.cursor.execute(
        'SELECT * FROM cpu ORDER BY ID DESC LIMIT 1'
    )
    cpu = build_dict(subscriber.storage.cursor,
                     subscriber.storage.cursor.fetchone())
    subscriber.storage.cursor.execute(
        'SELECT * FROM ram ORDER BY ID DESC LIMIT 1'
    )
    ram = build_dict(subscriber.storage.cursor,
                     subscriber.storage.cursor.fetchone())
    ret_val = {'memory': ram, 'cpu': cpu, 'network': network}
    return ret_val


class TestPersistence(unittest.TestCase):
    def setUp(self):
        clean_db()

    def test_persist_and_retrieve(self):
        metric_producer = metrics.MetricsCollector()
        data = metric_producer._collect()
        subscriber.data = data
        subscriber._save()
        ret_val = get_from_storage()
        for key in ['memory', 'cpu', 'network']:
            for sub_key in data[key]:
                sent = data[key][sub_key]
                retrieved = ret_val[key][sub_key]
                if type(retrieved) == decimal.Decimal:
                    retrieved = float(retrieved)
                err_msg = f'Values differ for {key} on {sub_key}'
                self.assertAlmostEqual(sent, retrieved, 2, err_msg)

    def tearDown(self):
        clean_db()
