import aiohttp
import asyncio
import time
import re
import json
import logging
from kafka import KafkaProducer
from datetime import datetime

from configs.configs import URLS, KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC, KAFKA_SSL_KEY, KAFKA_SSL_CERTIFICATE, KAFKA_SSL_CA, KAFKA_PASSWORD

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

producer = KafkaProducer(
    bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}',
    security_protocol='SSL',
    ssl_cafile=KAFKA_SSL_CA,
    ssl_certfile=KAFKA_SSL_CERTIFICATE,
    ssl_keyfile=KAFKA_SSL_KEY,
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    ssl_password=KAFKA_PASSWORD,
    key_serializer=lambda x: json.dumps(x).encode('utf-8'),
    api_version=(0, 10, 1)
)

def date_format(s):
    d_format = '%d %B %Y %H:%M:%S'
    return str(datetime.strptime(s, d_format))

async def request(url, session):
    start = time.perf_counter()
    site_data = {}
    current_time = datetime.now()
    r_sent_date = current_time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        async with session.get(url) as resp:
            current_time = datetime.now()
            r_response_date = current_time.strftime('%Y-%m-%d %H:%M:%S')
            r = await resp.text()
            status = resp.status
            try:
                title = re.findall('<title.*?>(.*?)</title>', r)[0]
            except:
                title = 'N/A'
            WEB_METRICS = {
                'url': str(resp.url),
                'name': str(resp.host),
                'title': title,
                'error_code': resp.status,
                'error_reason': resp.reason,
                'elapse_time': f'{time.perf_counter() - start:.5f}',
                'http_response_header_time': date_format(re.findall('Date.*?,\s(.*?)\sGMT', str(resp.start))[0]),
                'http_response_time': r_response_date, 
            }
            producer.send(KAFKA_TOPIC, value=WEB_METRICS)
    except Exception as e:
        logging.error(e)
    await asyncio.sleep(30)

async def main():
    timeout = aiohttp.ClientTimeout(total=60)
    
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []
        for url in URLS:
            tasks.append(asyncio.create_task(request(url.strip(), session)))
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(main())

