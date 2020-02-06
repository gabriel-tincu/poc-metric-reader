import pub_sub
import settings
import logging
log = logging.getLogger(__name__)

if __name__ == '__main__':
    pull_config = {
        'topics': settings.KAFKA_TOPIC,
        'bootstrap_servers': settings.KAFKA_HOST
    }
    push_config = {
        'connection_string': settings.POSTGRES_URI
    }
    sub = pub_sub.MetricSubscriber(
        pull_config=pull_config,
        push_config=push_config,
    )
    log.info('Launching metric collector')
    sub.consume()
