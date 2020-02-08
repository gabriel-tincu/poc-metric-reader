import kafka
from kafka.admin import NewTopic
import settings
import logging
import copy
log = logging.getLogger(__name__)


def delete_topic(name):
    cfg = copy.copy(settings.KAFKA_CONFIG)
    del cfg['topics']
    del cfg['consumer_timeout_ms']
    admin = kafka.KafkaAdminClient(**cfg)
    log.info(f'Attempting to delete topic {name}')
    try:
        admin.delete_topics([name])
    except Exception as e:
        log.info(e)


def create_topic(name):
    cfg = copy.copy(settings.KAFKA_CONFIG)
    del cfg['topics']
    del cfg['consumer_timeout_ms']
    admin = kafka.KafkaAdminClient(**cfg)
    topic = NewTopic(name, 1, 1)
    log.info(f'Attempting to create topic {name}')
    try:
        admin.create_topics([topic])
    except Exception as e:
        log.info(e)


