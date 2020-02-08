#!/usr/bin/env bash
folder=$(dirname $0)
image="metrics_homework:latest"
if ! docker build -t ${image} -f ${folder}/Dockerfile ${folder} ; then
    echo "Unable to build docker image"
    exit 1
fi
source ${folder}/env

if [[ -z ${KAFKA_KEY_FILE} || -z ${KAFKA_CERT_FILE} || -z ${KAFKA_CACERT_FILE} || -z ${KAFKA_HOST} || -z ${KAFKA_TOPIC} || -z ${PGURI} ]]; then
    echo "env file is not properly populated, please fill in the values"
    exit 1
fi

if [[ ! -f ${KAFKA_KEY_FILE} || ! -f ${KAFKA_CERT_FILE} || ! -f ${KAFKA_CACERT_FILE} ]]; then
    echo "The kafka key and cert files should point to valid disk files"
    exit 1
fi

key_folder=$(dirname ${KAFKA_KEY_FILE})
cert_folder=$(dirname ${KAFKA_CERT_FILE})
ca_folder=$(dirname ${KAFKA_CACERT_FILE})

e=" -e KAFKA_KEY_FILE=${KAFKA_KEY_FILE} -e KAFKA_CERT_FILE=${KAFKA_CERT_FILE} -e KAFKA_TOPIC=${KAFKA_TOPIC}"
e=${e}" -e KAFKA_CACERT_FILE=${KAFKA_CACERT_FILE} -e KAFKA_HOST=${KAFKA_HOST} -e PGURI=${PGURI}"
e=${e}" -e KAFKA_SECURITY_PROTOCOL=${KAFKA_SECURITY_PROTOCOL}"

vol="-v ${KAFKA_CACERT_FILE}:${KAFKA_CACERT_FILE} -v ${KAFKA_KEY_FILE}:${KAFKA_KEY_FILE} -v ${KAFKA_CERT_FILE}:${KAFKA_CERT_FILE}"

run-tests() {
    echo "docker run --rm -it ${e} ${image}"
    docker run --rm -it ${e} ${vol} ${image}
}

run-publisher() {
    docker run --rm -it ${e} ${vol} ${image} python publisher.py
}

run-subscriber() {
    docker run --rm -it ${e} ${vol} ${image} python subscriber.py
}

psql ${PGURI} -f init.sql
case $1 in
    tests)
        run-tests
    ;;
    publisher)
        run-publisher
    ;;
    subscriber)
        run-subscriber
    ;;
    *) echo "Unrecognised command"
       exit 1
    ;;
esac