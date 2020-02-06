import metrics
import kafka
import settings
import json
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
        self.publisher = publisher_class(**publisher_config)

    def publish_one(self, wait=True):
        self.generate_payload()
        log.info(f'sending {self.payload} on topic {self.topics}')
        f = self.publisher.send(self.topics, self.payload)
        if wait:
            result = f.get(timeout=self.push_timeout)
            log.info(f'Message successfully sent: {result}')
            return result

    def generate_payload(self):
        data = next(self.metric_generator)
        log.debug('New data from os metric collector {}'.format(data))
        self.payload = json.dumps(data).encode()

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
            log.debug(f"storing memory data {metric_data['memory']}")
            self.cursor.execute(
                'INSERT INTO RAM (total, available, used, free, percent) '
                'VALUES (%(total)s, %(available)s, '
                '%(used)s, %(free)s, %(percent)s)',
                metric_data['memory']
            )
            self.cursor.execute(
                'INSERT INTO SWAP (total, used, free, percent) '
                'VALUES (%(total)s, %(used)s, '
                '%(free)s, %(percent)s)',
                metric_data['swap']
            )
            self.cursor.execute(
                'INSERT INTO CPU (percent, idle, system, usr) '
                'VALUES (%(percent)s, %(idle)s, '
                '%(system)s, %(user)s)',
                metric_data['cpu']
            )
            self.cursor.execute(
                'INSERT INTO NETWORK (bytes_sent, bytes_recv) '
                'VALUES (%(bytes_sent)s, %(bytes_recv)s)',
                metric_data['network']
            )
            for dev_data in metric_data['disk']:
                self.cursor.execute(
                    'INSERT INTO DISK '
                    '(device, mountpoint, total, used, free, percent) '
                    'VALUES (%(device)s, %(mountpoint)s, '
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
        self.data = None
        self.storage = storage_class(**push_config)
        topics = pull_config.get('topics')
        if topics:
            del pull_config['topics']
        log.info('Initializing consumer')
        self.provider = pull_class(topics, **pull_config)

    def consume_forever(self):
        while True:
            try:
                self.consume_one()
            except Exception as e:
                log.exception(e)

    def produce_data(self):
        log.info(f'Waiting for a message on {self.provider.topics()}')
        message = next(self.provider)
        log.info(
            f'Got message with key {message.key} off topic {message.topic}')
        self.data = message.value

    def consume_one(self):
        self.produce_data()
        self._save()

    def _save(self):
        if not self.data:
            return
        data = json.loads(self.data.decode())
        log.info('New message off queue: {}'.format(data))
        res = self.storage.save(data)
        log.info('Message successfully saved')
        return res
