import os
import time
import logging
import logging.handlers


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
    return logger


def parameterized_decorator(decorator):
    def layer(*args, **kwargs):
        def repl(func):
            return decorator(func, *args, **kwargs)
        return repl
    return layer


@ parameterized_decorator
def run_time_decorator(func, logger):
    def run_time(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug('Time taken to run the function {}: {} seconds'.format(func.__name__, end_time - start_time))
        return result
    return run_time


@ parameterized_decorator
def retry_decorator(func, checker, num_retry, sleep_time, logger):
    def retry(*args, **kwargs):
        count = 0
        run_success = False
        response = {'status': False, 'terminate': False, 'message': 'Function {} not run yet'.format(func.__name__)}
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
                        'Terminate after attempt for function {}: {}'.format(
                            count + 1, func.__name__, checker(response)['message']))
                    count = num_retry
            else:
                run_success = True
        return response
    return retry
                




