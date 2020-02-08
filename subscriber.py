import pub_sub
import settings
import logging
log = logging.getLogger(__name__)

if __name__ == '__main__':
    push_config = {
        'connection_string': settings.POSTGRES_URI
    }
    pub_sub.create_topic(settings.KAFKA_TOPIC)
    sub = pub_sub.MetricSubscriber(
        pull_config=settings.KAFKA_CONFIG,
        push_config=push_config,
    )
    log.info('Launching metric collector')
    sub.consume_forever()
