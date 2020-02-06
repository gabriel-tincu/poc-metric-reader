import os
KAFKA_HOST = os.getenv('KAFKA_HOST', '192.168.178.34')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'metrics')
POSTGRES_HOST = os.getenv('PGHOST', 'postgres')
POSTGRES_USER = os.getenv('PGUSER', 'postgres')
POSTGRES_PASSWORD = os.getenv('PGPASSWORD', 'postgres')
POSTGRES_DATABASE = os.getenv('PGDATABASE', 'aiven')
POSTGRES_SSL = os.getenv('PGSSL', 'require')

POSTGRES_URI = f'host={POSTGRES_HOST} dbname={POSTGRES_DATABASE} ' \
    f'user={POSTGRES_USER} password={POSTGRES_PASSWORD} sslmode={POSTGRES_SSL}'

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