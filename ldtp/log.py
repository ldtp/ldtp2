"""
LDTP v2 client init file

@author: Eitan Isaacson <eitan@ascender.com>
@author: Nagappan Alagappan <nagappan@gmail.com>
@copyright: Copyright (c) 2009-13 Nagappan Alagappan
@copyright: Copyright (c) 2009 Eitan Isaacson
@license: LGPL

http://ldtp.freedesktop.org

This file may be distributed and/or modified under the terms of the GNU Lesser General
Public License version 2 as published by the Free Software Foundation. This file
is distributed without any warranty; without even the implied warranty of
merchantability or fitness for a particular purpose.

See 'COPYING' in the source distribution for more information.

Headers in this file shall remain intact.
"""

from os import environ as env
import logging

AREA = 'ldtp.client'
ENV_LOG_LEVEL = 'LDTP_LOG_LEVEL'
ENV_LOG_OUT = 'LDTP_LOG_OUT'
ENV_LOG_STYLE = 'LDTP_LOG_STYLE'


class noParsingFilter(logging.Filter):
    def filter(self, record):
        return record.getMessage().rfind('getlastlog()')

log_level = getattr(logging, env.get(ENV_LOG_LEVEL, 'NOTSET'), logging.NOTSET)

logger = logging.getLogger(AREA)

if ENV_LOG_OUT not in env:
    handler = logging.StreamHandler()
    if ENV_LOG_STYLE in env and env[ENV_LOG_STYLE].lower() == 'short':
        handler.setFormatter(
            logging.Formatter('%(name)-11s %(levelname)-8s %(message)s'))
    else:
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
else:
    handler = logging.FileHandler(env[ENV_LOG_OUT])
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))

logger.addHandler(handler)

logger.addFilter(noParsingFilter())

logger.setLevel(log_level)
