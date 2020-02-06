import os

KAFKA_HOST = os.getenv('KAFKA_HOST', 'kafka-949fc5e-gabriel-d381.aivencloud.com:24507')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'metrics')
POSTGRES_URI = os.getenv('POSTGRES_URI', 'host=postgres dbname=aiven '
                         'user=postgres password=postgres')