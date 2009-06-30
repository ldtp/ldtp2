from os import environ as env
import logging

AREA = 'ldtp.client'
ENV_LOG_LEVEL = 'LDTP_LOG_LEVEL'

log_level = getattr(logging, env.get(ENV_LOG_LEVEL, 'NOTSET'), logging.NOTSET)

logger = logging.getLogger('ldtp.client')

handler = logging.StreamHandler()

handler.setFormatter(
    logging.Formatter('%(name)-11s: %(levelname)-8s %(message)s'))

logger.addHandler(handler)

logger.setLevel(log_level)
