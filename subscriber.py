import util
import logging
import kafka
import settings
import copy
from json import loads, JSONDecodeError
import psycopg2
log = logging.getLogger(__name__)


class MessageDecodeException(Exception):
    pass


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
            raise MessageDecodeException(
                f'Badly formatted message: {self.raw_data}'
            )

    def _save(self):
        if not self.data:
            return
        log.info('New message off queue: {}'.format(self.data))
        res = self.storage.save(self.data)
        log.info('Message successfully saved')
        return res


if __name__ == '__main__':
    push_config = {
        'connection_string': settings.POSTGRES_URI
    }
    util.create_topic(settings.KAFKA_TOPIC)
    sub = MetricSubscriber(
        pull_config=settings.KAFKA_CONFIG,
        push_config=push_config,
    )
    log.info('Launching metric collector')
    sub.consume_forever()
