import os


if os.getenv('GAE_ENV', '') or os.getenv('DEBUG_STATUS', '') == '0':
    DEBUG = False
else:
    DEBUG = True

# template variable
if DEBUG:
    ROOT_URL = 'http://localhost:8080'
else:
    ROOT_URL = 'https://mathquiz.pythoner.work'
