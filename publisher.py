import pub_sub
import logging
import settings
log = logging.getLogger(__name__)

if __name__ == '__main__':
    config = {
        'topic': settings.KAFKA_TOPIC,
        'host': settings.KAFKA_HOST
    }
    pub = pub_sub.MetricPublisher(publisher_config=config)
    log.info('Launching metric collector')
    pub.publish_forever()
