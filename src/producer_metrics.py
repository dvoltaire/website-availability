import aiohttp
import asyncio
import time
import re
import json
from kafka import KafkaProducer, KafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from datetime import datetime

from configs.log import log
from configs.configs import (
    URLS,
    KAFKA_HOST,
    KAFKA_PORT,
    KAFKA_TOPIC,
    KAFKA_SSL_KEY,
    KAFKA_SSL_CERTIFICATE,
    KAFKA_SSL_CA,
    KAFKA_PASSWORD,
)

# Initializize client
kafka_client = KafkaClient(
    bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
    security_protocol="SSL",
    ssl_cafile=KAFKA_SSL_CA,
    ssl_certfile=KAFKA_SSL_CERTIFICATE,
    ssl_keyfile=KAFKA_SSL_KEY,
    ssl_password=KAFKA_PASSWORD,
)

kafka_admin = KafkaAdminClient(
    bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
    security_protocol="SSL",
    ssl_cafile=KAFKA_SSL_CA,
    ssl_certfile=KAFKA_SSL_CERTIFICATE,
    ssl_keyfile=KAFKA_SSL_KEY,
    ssl_password=KAFKA_PASSWORD,
)

kafka_producer = KafkaProducer(
    bootstrap_servers=f"{KAFKA_HOST}:{KAFKA_PORT}",
    security_protocol="SSL",
    ssl_cafile=KAFKA_SSL_CA,
    ssl_certfile=KAFKA_SSL_CERTIFICATE,
    ssl_keyfile=KAFKA_SSL_KEY,
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    ssl_password=KAFKA_PASSWORD,
    key_serializer=lambda x: json.dumps(x).encode("utf-8"),
)
# Do not assume the Kafka topic is already created.
# This will create a default kafka topic with 3 partitions, and a replication factor 3..
try:
    future = kafka_client.cluster.request_update()
    kafka_client.poll(future=future)

    metadata = kafka_client.cluster

    new_topic = [NewTopic(KAFKA_TOPIC, num_partitions=3, replication_factor=3)]
    if not KAFKA_TOPIC in metadata.topics():
        log.info("Create a new topic")
        kafka_admin.create_topics(new_topic, validate_only=False)
        time.sleep(10)
except Exception as e:
    log.error(e)


def date_format(s):
    d_format = "%d %B %Y %H:%M:%S"
    return str(datetime.strptime(s, d_format))


async def produce_message(WEB_METRICS):
    kafka_producer.send(KAFKA_TOPIC, value=WEB_METRICS)


async def request(url, session):
    try:
        async with session.get(url) as resp:
            current_time = datetime.now()
            start = time.time()
            r_date_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            r_text = await resp.text()
            status = resp.status
            try:
                title = re.findall("<title.*?>(.*?)</title>", r_text)[0]
            except:
                title = "N/A"
            WEB_METRICS = {
                "url": str(resp.url),
                "name": str(resp.host),
                "title": title,
                "error_code": resp.status,
                "error_reason": resp.reason,
                "elapse_time": f"{(time.time() - start):.5f}",
                "http_response_time": r_date_time,
            }
            try:
                await asyncio.wait_for(produce_message(WEB_METRICS), timeout=10)
            except:
                pass
    except Exception as e:
        log.warning(e)
    await asyncio.sleep(60)


async def main():
    timeout = aiohttp.ClientTimeout(total=60)

    connector = aiohttp.TCPConnector(ssl=False, use_dns_cache=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for url in URLS:
            tasks.append(asyncio.create_task(request(url.strip(), session)))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(main())
