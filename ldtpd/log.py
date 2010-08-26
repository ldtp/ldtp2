from os import environ as env
import logging

AREA = 'ldtp.server'
ENV_LOG_LEVEL = 'LDTPD_LOG_LEVEL'
ENV_LOG_OUT = 'LDTPD_LOG_OUT'

log_level = getattr(logging, env.get(ENV_LOG_LEVEL, 'NOTSET'), logging.NOTSET)

logger = logging.getLogger(AREA)

if ENV_LOG_OUT not in env:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(name)-11s %(levelname)-8s %(message)s'))
else:
    handler = logging.FileHandler(env[ENV_LOG_OUT])
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))

logger.addHandler(handler)

logger.setLevel(log_level)
