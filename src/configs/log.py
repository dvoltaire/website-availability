# A very basic logs
from logging import getLogger, basicConfig, INFO
from datetime import datetime
import os
__all__ = ['log']

path, _ = os.path.split(os.path.realpath(__file__))
os.chdir(path)

current_date = datetime.now().strftime("%Y%m%d")
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
LOG_DIR = f'../../logs/{current_date}.log'
log = getLogger(__name__)


log_format = '%(asctime)s:%(levelname)s:%(name)s:(%(funcName)s:%(lineno)d):%(message)s'
basicConfig(level=INFO, filename=LOG_DIR, filemode='a', format=log_format)
#log.error('Test')
