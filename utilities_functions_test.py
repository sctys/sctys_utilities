import os
import sys
import inspect
from utilities_functions import set_logger, run_time_wrapper
sys.path.append(os.environ['SCTYS_PROJECT'] + '/sctys_global_parameters')
from global_parameters import Path


def test_logger():
    logger_path = Path.LOG_FOLDER + '/log_sctys_utilities'
    logger_file_name = inspect.currentframe().f_code.co_name + '.log'
    logger_name = inspect.currentframe().f_code.co_name
    logger_level = 'DEBUG'
    logger = set_logger(logger_path, logger_file_name, logger_level, logger_name)
    for i in range(10):
        logger.debug('Testing {}'.format(i))


def test_time_wrapper():
    logger_path = Path.LOG_FOLDER + '/log_sctys_utilities'
    logger_file_name = inspect.currentframe().f_code.co_name + '.log'
    logger_name = inspect.currentframe().f_code.co_name
    logger_level = 'DEBUG'
    logger = set_logger(logger_path, logger_file_name, logger_level, logger_name)

    def test_loop(n):
        i_sum = 0
        for i in range(n):
            i_sum += i
        return i_sum
    n_sum = run_time_wrapper(test_loop, logger)(100)

    logger.debug('Sum = {}'.format(n_sum))


if __name__ == '__main__':
    # test_logger()
    test_time_wrapper()