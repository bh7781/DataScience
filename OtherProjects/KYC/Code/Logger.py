# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 15:09:58 2019

@author: aarora33
"""

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
import json
import logging.config

def setup_logging(
    default_path='Logger_Config.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        
logger_config = r"Logger_Config.json"
setup_logging(logger_config, logging.ERROR, '')

logger = logging.getLogger()
print('-----', logger)
logger.error('often makes a very good meal of %s', 'visiting tourists')