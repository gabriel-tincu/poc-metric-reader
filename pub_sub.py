import metrics
import kafka
import settings
from json import loads, dumps, JSONDecodeError
import psycopg2
import logging
import copy
log = logging.getLogger(__name__)


class MetricPublisher:
    def __init__(
            self,
            publisher_config,
            publisher_class=kafka.KafkaProducer):
        self.payload = None
        publisher_config = copy.copy(publisher_config)
        self.topics = publisher_config.get('topics', 'metrics')
        if 'topics' in publisher_config:
            del publisher_config['topics']
        self.push_timeout = publisher_config.get('timeout', 60)
        if 'timeout' in publisher_config:
            del publisher_config['timeout']
        self.publisher_class = publisher_class
        self.metric_generator = metrics.MetricsCollector().gather()
        if 'consumer_timeout_ms' in publisher_config:
            del publisher_config['consumer_timeout_ms']
        self.publisher = publisher_class(**publisher_config)

    def publish_one(self):
        self.generate_payload()
        log.info(f'sending {self.payload} on topic {self.topics}')
        return self.publisher.send(self.topics, self.payload, partition=0)

    def generate_payload(self):
        data = next(self.metric_generator)
        log.debug('New data from os metric collector {}'.format(data))
        self.payload = dumps(data).encode()

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
        for k in ['memory', 'swap', 'cpu', 'network']:
            metric_data[k]['host'] = metric_data['name']
        for entry in metric_data['disk']:
            entry['host'] = metric_data['name']
        try:
            log.debug(f"storing memory data {metric_data['memory']}")
            self.cursor.execute(
                'INSERT INTO RAM (host, total, available, used, free, percent) '
                'VALUES (%(host)s, %(total)s, %(available)s, '
                '%(used)s, %(free)s, %(percent)s)',
                metric_data['memory']
            )
            self.cursor.execute(
                'INSERT INTO SWAP (host, total, used, free, percent) '
                'VALUES (%(host)s, %(total)s, %(used)s, '
                '%(free)s, %(percent)s)',
                metric_data['swap']
            )
            self.cursor.execute(
                'INSERT INTO CPU (host, percent, idle, system, usr) '
                'VALUES (%(host)s, %(percent)s, %(idle)s, '
                '%(system)s, %(usr)s)',
                metric_data['cpu']
            )
            self.cursor.execute(
                'INSERT INTO NETWORK (host, bytes_sent, bytes_recv) '
                'VALUES (%(host)s, %(bytes_sent)s, %(bytes_recv)s)',
                metric_data['network']
            )
            for dev_data in metric_data['disk']:
                self.cursor.execute(
                    'INSERT INTO DISK '
                    '(host, device, mountpoint, total, used, free, percent) '
                    'VALUES (%(host)s, %(device)s, %(mountpoint)s, '
                    '%(total)s, %(used)s, %(free)s, %(percent)s)',
                    dev_data
                )

            self.conn.commit()
        except:
            self.conn.rollback()
            raise


class MetricSubscriber:
    def __init__(
            self,
            pull_config,
            push_config,
            pull_class=kafka.KafkaConsumer,
            storage_class=PostgresStorage
    ):
        pull_config = copy.copy(pull_config)
        push_config = copy.copy(push_config)
        self.raw_data = None
        self.data = None
        self.storage = storage_class(**push_config)
        topics = pull_config.get('topics')
        if topics:
            del pull_config['topics']
        log.info('Initializing consumer')
        self.provider = pull_class(group_id='subscriber', **pull_config)
        log.info(f'assigning topic {topics} partition 0')
        self.provider.assign([kafka.TopicPartition(topics, 0)])

    def consume_forever(self):
        while True:
            try:
                self.consume_one()
            except Exception as e:
                log.exception(e)

    def read_message(self):
        log.info(f'Waiting for a message on {self.provider.assignment()}')
        message = next(self.provider)
        log.info(
            f'Got message with key {message.key} off topic {message.topic}')
        self.raw_data = message.value

    def consume_one(self):
        self.read_message()
        self._decode()
        self._save()

    def _decode(self):
        try:
            self.data = loads(self.raw_data.decode())
        except JSONDecodeError:
            raise Exception(f'Badly formatted message: {self.raw_data}')

    def _save(self):
        if not self.data:
            return
        log.info('New message off queue: {}'.format(self.data))
        res = self.storage.save(self.data)
        log.info('Message successfully saved')
        return res
