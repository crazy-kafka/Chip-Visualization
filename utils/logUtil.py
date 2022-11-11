from __future__ import annotations
from typing import List, Tuple, Dict, Union, Iterable, TYPE_CHECKING, AnyStr

if TYPE_CHECKING:
    pass

import logging
import os
from .globalVariable import GlobalVariable


def setup_logger(name, log_file, format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, out_to_console=False):

    formatter = logging.Formatter(format)

    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if out_to_console is True:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger


def logInitialize(out_log_patt=''):
    log_file = 'proton.log'
    cmd_file = 'proton.cmd'
    if out_log_patt:
        if os.path.isdir(out_log_patt):
            dir_name = out_log_patt
            base_name = log_file
        else:
            dir_name = os.path.dirname(out_log_patt)
            base_name = os.path.basename(out_log_patt)

            if not base_name:
                base_name = 'proton.log'

            if dir_name:
                os.system(f'mkdir -p {dir_name}')
            else:
                dir_name = '.'

            if not base_name.endswith('.log'):
                base_name += '.log'

        log_file = dir_name + '/' + base_name
        cmd_file = dir_name + '/' + base_name.replace('.log', '.cmd')

    GlobalVariable.BASE_LOGGER = setup_logger('log', log_file)
    GlobalVariable.LOG_CMD_LOGGER = setup_logger('log', log_file)
    GlobalVariable.CMD_LOGGER = setup_logger('cmd', cmd_file, format='%(message)s')

    GlobalVariable.NO_LOG = False


def Print(msg: AnyStr, level='info'):
    if level == 'error':
        print(f'ERROR: ' + msg)
    elif level == 'warning':
        print(f'WARNING: ' + msg)
    else:
        print(msg)
    if GlobalVariable.NO_LOG is False:
        logger = GlobalVariable.BASE_LOGGER
        if level == 'debug':
            logger.debug(msg)
        elif level == 'info':
            logger.info(msg)
        elif level == 'warning':
            logger.warning(msg)
        elif level == 'error':
            logger.error(msg)
        elif level == 'critical':
            logger.critical(msg)






