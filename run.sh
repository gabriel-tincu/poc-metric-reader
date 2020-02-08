#!/usr/bin/env bash
folder=$(dirname $0)
if [[ ! -f "${folder}/venv/bin/activate" ]]; then
    rm -rf ${folder}/venv
    virtualenv ${folder}/venv --python python3
fi
source ${folder}/venv/bin/activate
pip install -r ${folder}/requirements.txt
source ${folder}/env

if [[ -z ${KAFKA_KEY_FILE} || -z ${KAFKA_CERT_FILE} || -z ${KAFKA_CACERT_FILE} || -z ${KAFKA_HOST} || -z ${KAFKA_TOPIC} || -z ${PGURI} ]]; then
    echo "env file is not properly populated, please fill in the values"
    exit 1
fi

if [[ ! -f ${KAFKA_KEY_FILE} || ! -f ${KAFKA_CERT_FILE} || ! -f ${KAFKA_CACERT_FILE} ]]; then
    echo "The kafka key and cert files should point to valid disk files"
    exit 1
fi
echo ${folder}
case $1 in
    tests)
        c=$(pwd)
        cd ${folder}
        psql ${PGURI} -f init.sql
        python -m unittest
        status=$?
        cd ${c}
        exit ${status}
    ;;
    publisher)
        python ${folder}/publisher.py
    ;;
    subscriber)
        python ${folder}/subscriber.py
    ;;
    *) echo "Unrecognised command"
       exit 1
    ;;
esac

trap 0 1