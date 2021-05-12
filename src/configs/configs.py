import os
import yaml
import sys
from glob import glob
from log import log

__all__ = [
    "DB_SERVER",
    "DB_USERNAME",
    "DB_PORT",
    "DB_NAME",
    "DB_TABLE",
    "DB_PASSWORD",
    "KAFKA_PASSWORD",
    "KAFKA_HOST",
    "KAFKA_PORT",
    "KAFKA_TOPIC",
    "KAFKA_SSL_KEY",
    "KAFKA_SSL_CERTIFICATE",
    "KAFKA_SSL_CA",
    "URLS",
]

path, _ = os.path.split(os.path.realpath(__file__))

os.chdir(path)


def get_file_path(name):
    filename = glob(name)
    if len(filename) != 1:
        log.error(
            f"Ambiguity, We expext only 5 files, one of each"
            "[*.txt(2), *.key, *.cert, *.pem] end in secrets/ directory."
        )
    if filename:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), (glob(name)[0])))
    return name


KAFKA_SSL_KEY = get_file_path("../../confd/secrets/*.key")
KAFKA_SSL_CERTIFICATE = get_file_path("../../confd/secrets/*.cert")
KAFKA_SSL_CA = get_file_path("../../confd/secrets/*.pem")
config_yaml = get_file_path("../../confd/config.yaml")
database_password = get_file_path("../../confd/secrets/*.db")
kafka_password = get_file_path("../../confd/secrets/*.ka")
urls = get_file_path("../../confd/website_urls.txt")


def load_configs():
    try:
        with open(database_password) as dbpasswd, open(config_yaml) as stream, open(
            urls
        ) as url_file, open(kafka_password) as kfpassword:
            return [
                dbpasswd.read().strip(),
                kfpassword.read().strip(),
                yaml.safe_load(stream),
                [url.strip() for url in url_file.readlines()],
            ]
    except Exception as e:
        log.error(e)
        sys.exit(101)


DB_PASSWORD, KAFKA_PASSWORD, CONFIG, URLS = load_configs()

postgres = CONFIG["POSTGRES"]
kafka = CONFIG["KAFKA"]

DB_SERVER = postgres["DB_SERVER"]
DB_USERNAME = postgres["DB_USER"]
DB_PORT = postgres["DB_PORT_NUMBER"]
DB_NAME = postgres["DB_NAME"]
DB_TABLE = postgres["DB_TABLE"]
KAFKA_HOST = kafka["KAFKA_BOOTSTRAP_SERVERS"]
KAFKA_PORT = kafka["KAFKA_PORT_NUMBER"]
KAFKA_TOPIC = kafka["KAFKA_TOPIC"]
