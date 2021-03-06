import logging

from config import LOG_FILE

# Courtesy https://stackoverflow.com/a/49562361
log = logging.getLogger('discord')
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
)

# Log to File
fh = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)

# Log to Console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
log.addHandler(ch)
