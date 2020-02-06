from pub_sub import *
import unittest
import settings
import json
import copy
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
    def send(topic, data):
        return MockFuture(data)


class MockSubscriber:
    def __init__(self, *args, **kwargs):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        return mock_type('key', 'prov', 'metrics', mock_message)

    def poll(self, duration):
        return [mock_type('key', 'prov', 'metrics', mock_message)]

    def topics(self):
        return {'test'}


class MockStorage:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def save(data):
        return data


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
        sent = json.loads(res.decode())
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
        data = self.subscriber.data
        self.assertIsNotNone(data)