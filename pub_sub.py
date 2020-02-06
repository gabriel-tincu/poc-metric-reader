import metrics
import kafka
import settings
import json
import psycopg2
import logging
log = logging.getLogger(__name__)


class MetricPublisher:
    def __init__(
            self,
            publisher_config,
            publisher_class=kafka.KafkaProducer):
        self.topic = publisher_config.get('topic', 'metrics')
        self.push_timeout = publisher_config.get('timeout', 60)
        self.publisher_class = publisher_class
        self.metric_generator = metrics.MetricsCollector().gather()
        host = publisher_config.get('host', 'localhost')
        log.info(f'Launching publisher for kafka host {host} and topic {self.topic}')
        self.publisher = publisher_class(
            bootstrap_servers=publisher_config.get('host', 'localhost')
        )

    def publish_one(self, wait=True):
        data = next(self.metric_generator)
        to_bytes = json.dumps(data).encode()
        f = self.publisher.send(self.topic, to_bytes)
        if wait:
            f.get(timeout=self.push_timeout)

    def publish_forever(self):
        while True:
            try:
                self.publish_one()
            except Exception as e:
                log.exception(e)


class PostgresStorage:
    def __init__(self, connection_string=settings.POSTGRES_URI):
        self.conn = psycopg2.connect(connection_string)
        self.cursor = self.conn.cursor()

    def save(self, metric_data):
        try:
            self.cursor.execute(
                'INSERT INTO RAM VALUES (%(total), %(available), '
                '%(used), %(free) ,%(percent))',
                metric_data['memory']
            )
            self.cursor.execute(
                'INSERT INTO SWAP VALUES (%(total), %(used), '
                '%(free) ,%(percent))',
                metric_data['swap']
            )
            self.cursor.execute(
                'INSERT INTO CPU VALUES (%(percent), %(idle), '
                '%(system) ,%(user))',
                metric_data['cpu']
            )
            self.cursor.execute(
                'INSERT INTO NETWORK VALUES (%(bytes_sent), %(bytes_recv)',
                metric_data['network']
            )
            for dev_data in metric_data['disk']:
                self.cursor.execute(
                    'INSERT INTO DISK VALUES (%(device), %(mountpoint), '
                    '%(total) ,%(used), %(free), %(percent))',
                    dev_data
                )

            self.conn.commit()
        except Exception as e:
            log.exception(e)
        finally:
            self.conn.rollback()


class MetricSubscriber:
    def __init__(
            self,
            pull_config,
            push_config,
            pull_class=kafka.KafkaConsumer,
            storage_class=PostgresStorage
    ):
        self.storage = storage_class(**push_config)
        topics = pull_config.get('topics')
        if topics:
            del pull_config['topics']
        self.provider = pull_class(topics, **pull_config)

    def consume(self):
        for byte_data in self.provider:
            try:
                self._save(byte_data)
            except Exception as e:
                log.exception(e)

    def consume_one(self):
        byte_data = next(self.provider)
        self._save(byte_data)

    def _save(self, byte_data):
        data = json.loads(byte_data.decode())
        self.storage.save(data)
