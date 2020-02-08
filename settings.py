import os
KAFKA_HOST = os.getenv('KAFKA_HOST', '192.168.178.34')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'metrics')
POSTGRES_URI = os.getenv('PGURI', 'postgres://postgres:postgres@localhost:5432/postgres?sslmode=prefer')

KAFKA_CONSUMER_TIMEOUT=int(os.getenv('KAFKA_CONSUMER_TIMEOUT', 5000))
KAFKA_KEY_FILE = os.getenv('KAFKA_KEY_FILE')
KAFKA_CERT_FILE = os.getenv('KAFKA_CERT_FILE')
KAFKA_CACERT_FILE = os.getenv('KAFKA_CACERT_FILE')
KAFKA_SECURITY_PROTOCOL = os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT')

KAFKA_CONFIG = {
    'topics': KAFKA_TOPIC,
    'bootstrap_servers': KAFKA_HOST,
    'security_protocol': KAFKA_SECURITY_PROTOCOL,
    'ssl_certfile': KAFKA_CERT_FILE,
    'ssl_keyfile': KAFKA_KEY_FILE,
    'ssl_cafile': KAFKA_CACERT_FILE,
    'consumer_timeout_ms': KAFKA_CONSUMER_TIMEOUT
}