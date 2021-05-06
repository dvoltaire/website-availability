import psycopg2
import time
import re
import json
import logging
from kafka import KafkaConsumer
from datetime import datetime

from configs.configs import URLS, KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC, KAFKA_SSL_KEY, \
        KAFKA_SSL_CERTIFICATE, KAFKA_SSL_CA, KAFKA_PASSWORD, DB_SERVER, \
        DB_PORT, DB_NAME, DB_TABLE, DB_USERNAME, DB_PASSWORD

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}',
    security_protocol='SSL',
    ssl_cafile=KAFKA_SSL_CA,
    ssl_certfile=KAFKA_SSL_CERTIFICATE,
    ssl_keyfile=KAFKA_SSL_KEY,
    ssl_password=KAFKA_PASSWORD,
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    api_version=(0, 10, 1),
    group_id=f'{KAFKA_TOPIC}_00'
)

SQL = f"INSERT INTO {DB_TABLE}(url, name, page_title, error_code, error_reason, elapse_time, http_response_header_time, http_response_time)"


commands = (
    '''
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    ''',
    f'''
        CREATE TABLE IF NOT EXISTS {DB_TABLE}(
                id uuid DEFAULT uuid_generate_v4(),
                url VARCHAR(255),
                name VARCHAR(255),
                page_title VARCHAR(255),
                error_code INTEGER,
                error_reason VARCHAR(255),
                elapse_time REAL,
                http_response_header_time TIMESTAMP,
                http_response_time TIMESTAMP
        );
    '''
)

def connect():
    try:

        conn = psycopg2.connect(
            host = DB_SERVER,
            port = DB_PORT,
            database = DB_NAME,
            user = DB_USERNAME,
            password = DB_PASSWORD
        )

        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
            conn.commit()

        cur = conn.cursor()
        for message in consumer:
            message = message.value
            VALUE = (
                message['url'],
                message['name'],
                message['title'].replace("'", '"'),
                message['error_code'],
                message['error_reason'],
                message['elapse_time'],
                message['http_response_header_time'],
                message['http_response_time']
            )

            cur.execute(f'{SQL} VALUES {VALUE};')
            conn.commit()
        conn.commit()
        return conn

    except Exception as error:
        logging.error(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    connect()

