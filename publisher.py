import util
import logging
import settings
import psutil
import os
import time
import copy
import kafka
from json import dumps
log = logging.getLogger(__name__)


class MetricsCollector:
    def __init__(self, collect_interval=1.9):
        self.host_name = None
        try:
            self.host_name = os.uname().nodename
        except:
            pass
        if not self.host_name:
            self.host_name = "default"
        self.collect_interval = collect_interval
        # first value will be nonsensical
        psutil.cpu_percent()

    def gather(self):
        while True:
            yield self._collect()
            time.sleep(self.collect_interval)

    def _collect(self):
        return {
            'memory': self._collect_ram(),
            'swap': self._collect_swap(),
            'disk': self._collect_disk(),
            'cpu': self._collect_cpu(),
            'network': self._collect_network(),
            'name': self.host_name
        }

    @staticmethod
    def _collect_ram():
        virt_mem = psutil.virtual_memory()
        return {
            'total': virt_mem.total,
            'available': virt_mem.available,
            'used': virt_mem.used,
            'free': virt_mem.free,
            'percent': virt_mem.percent
        }

    @staticmethod
    def _collect_swap():
        swap = psutil.swap_memory()
        return {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent
        }

    @staticmethod
    def _collect_cpu():
        cpu = psutil.cpu_times()
        return {
            'percent': psutil.cpu_percent(),
            'idle': cpu.idle,
            'system': cpu.system,
            'usr': cpu.user
        }

    @staticmethod
    def _collect_disk():
        # probably should add more types here
        # also, mapping between device and devices listed under
        collected_types = ['ext4']
        usage = []
        for part in [x for x in psutil.disk_partitions(True)
                     if x.fstype in collected_types]:
            part_usage = psutil.disk_usage(part.mountpoint)
            usage.append({
                'device': part.device,
                'mountpoint': part.mountpoint,
                'total': part_usage.total,
                'used': part_usage.used,
                'free': part_usage.free,
                'percent': part_usage.percent,
            })
        return usage

    @staticmethod
    def _collect_network():
        stats = psutil.net_io_counters()
        return {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
        }

class MetricPublisher:
    def __init__(
            self,
            publisher_config,
            publisher_class=kafka.KafkaProducer):
        self.payload = None
        self.admin = None
        publisher_config = copy.copy(publisher_config)
        self.topics = publisher_config.get('topics', 'metrics')
        if 'topics' in publisher_config:
            del publisher_config['topics']
        self.push_timeout = publisher_config.get('timeout', 60)
        if 'timeout' in publisher_config:
            del publisher_config['timeout']
        self.publisher_class = publisher_class
        self.metric_generator = MetricsCollector().gather()
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


if __name__ == '__main__':
    util.create_topic(settings.KAFKA_TOPIC)
    pub = MetricPublisher(publisher_config=settings.KAFKA_CONFIG)
    log.info('Launching metric collector')
    pub.publish_forever()
