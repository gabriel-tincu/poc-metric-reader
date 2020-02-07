import os
KAFKA_HOST = os.getenv('KAFKA_HOST', 'localhost')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'default-topic')
POSTGRES_URI = os.getenv('PGURI', 'postgres://postgres:postgres@localhost:5432/postgres?sslmode=prefer')

KAFKA_KEY_FILE = os.getenv('KAFKA_KEY_FILE', '/tmp/service.key')
KAFKA_CERT_FILE = os.getenv('KAFKA_CERT_FILE', '/tmp/service.cert')
KAFKA_CACERT_FILE = os.getenv('KAFKA_CACERT_FILE', '/tmp/ca.pem')

KAFKA_CONFIG = {
    'topics': KAFKA_TOPIC,
    'bootstrap_servers': KAFKA_HOST,
    'security_protocol': 'SSL',
    'ssl_certfile': KAFKA_CERT_FILE,
    'ssl_keyfile': KAFKA_KEY_FILE,
    'ssl_cafile': KAFKA_CACERT_FILE,
}