""" app_logger

flaskのログ関係の処理群
"""
import os
import datetime
import logging
import logging.handlers


def initialize_logger(logger):
    dt_now = datetime.datetime.now()
    str_dt = dt_now.strftime('%Y%m%d_%H%M%S')
    str_dir = dt_now.strftime('%Y/%Y%m')
    os.makedirs(f'./log/{str_dir}', exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(f'./log/{str_dir}/{str_dt}.log', 'a+', maxBytes=10000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info('launched!')

    return None


def write_info_log(logger, msg):
    logger.info(f'{msg}')
    return None


def write_error_log(logger, msg):
    logger.error(f'{msg}')
    return None

