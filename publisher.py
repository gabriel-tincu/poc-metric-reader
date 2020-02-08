import pub_sub
import logging
import settings
log = logging.getLogger(__name__)

if __name__ == '__main__':
    pub_sub.create_topic(settings.KAFKA_TOPIC)
    pub = pub_sub.MetricPublisher(publisher_config=settings.KAFKA_CONFIG)
    log.info('Launching metric collector')
    pub.publish_forever()
