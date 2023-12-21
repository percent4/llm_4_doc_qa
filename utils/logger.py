# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: logger.py
# @time: 2023/7/23 14:48
import os
import time
import json
from loguru import logger

from config.config_parser import PROJECT_DIR, LOG_PATH

log_dir = os.path.join(PROJECT_DIR, LOG_PATH)
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

t = time.strftime("%Y-%m-%d")
logger.add(f"{log_dir}/{t}_all.log",
           level="INFO",
           rotation="00:00",
           retention='90 days',
           format="{time} - {name} - {level} - {message}")

logger.add(f"{log_dir}/{t}_err.log",
           level="ERROR",
           filter=lambda x: 'ERROR' in str(x['level']).upper(),
           rotation="00:00",
           retention='90 days',
           format="{time} - {name} - {level} - {message}")
