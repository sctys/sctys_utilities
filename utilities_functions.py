import os
import time
import logging
import datetime
import pytz
import json
import re
import logging.handlers
import asyncio


def set_logger(logger_path, logger_file_name, logger_level, logger_name):
    logger_file = os.path.join(logger_path, logger_file_name)
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, logger_level))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=logger_file, when='D', interval=1, backupCount=180)
    file_handler.setLevel(getattr(logging, logger_level))
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(getattr(logging, logger_level))
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger = logging.getLogger(logger_name)
    return logger


def run_time_wrapper(func, logger):
    def run_time(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug('Time taken to run the function {}: {} seconds'.format(func.__name__, end_time - start_time))
        return result
    return run_time


def retry_wrapper(func, checker, num_retry, sleep_time, logger):
    def retry(*args, **kwargs):
        count = 0
        run_success = False
        response = {'ok': False, 'error': 'Function {} not run yet'.format(func.__name__)}
        while count < num_retry and not run_success:
            response = func(*args, **kwargs)
            if not checker(response)['status']:
                if not checker(response)['terminate']:
                    logger.error(
                        'Fail attempt {} for function {}: {}'.format(
                            count + 1, func.__name__, checker(response)['message']))
                    time.sleep(sleep_time)
                    count += 1
                else:
                    logger.error(
                        'Terminate after attempt {} for function {}: {}'.format(
                            count + 1, func.__name__, checker(response)['message']))
                    count = num_retry
            else:
                run_success = True
        if not run_success and response['ok']:
            response = {'ok': False, 'error': checker(response)['message']}
        return response
    return retry


def async_retry_wrapper(func, checker, num_retry, sleep_time, logger):
    async def async_retry(*args, **kwargs):
        count = 0
        run_success = False
        response = {'status': False, 'terminate': False, 'message': 'Function {} not run yet'.format(func.__name__)}
        while count < num_retry and not run_success:
            response = await func(*args, **kwargs)
            if not checker(response)['status']:
                if not checker(response)['terminate']:
                    logger.error(
                        'Fail attempt {} for function {}: {}'.format(
                            count + 1, func.__name__, checker(response)['message']))
                    await asyncio.sleep(sleep_time)
                    count += 1
                else:
                    logger.error(
                        'Terminate after attempt for function {}: {}'.format(
                            count + 1, func.__name__, checker(response)['message']))
                    count = num_retry
            else:
                run_success = True
        if not run_success and response['ok']:
            response = {'ok': False, 'error': checker(response)['message']}
        return response
    return async_retry


def error_notifier_wrapper(func, notifier):
    def error_notifier(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            notifier.retry_send_message('Error in {}: {}'.format(func.__name__, e))
            raise
    return error_notifier


def convert_datetime_to_timestamp(date_str, time_zone=None):
    if time_zone is not None:
        time_stamp = datetime.datetime.strptime(
            date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone(time_zone)).timestamp()
    else:
        time_stamp = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').timestamp()
    return int(time_stamp)


def clean_json_loads(text, additional_rules):
    text = text.replace("'", '"').replace('\t', ' ').replace('<br>', '').replace('""""', '""').replace('"""', '""')
    for origin, replacement in additional_rules.items():
        text = re.sub(origin, replacement, text)
    try:
        text = json.loads(text)
        return text
    except json.decoder.JSONDecodeError:
        print(text)
    



