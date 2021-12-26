import logging

from flask import Flask

import google.cloud.logging

from settings import DEBUG
from views import *


app = Flask(__name__)


app.add_url_rule('/', \
        view_func=IndexView.as_view('index'))
app.add_url_rule('/a_plus_b', \
        view_func=APlusBView.as_view('a_plus_b'))


if __name__ == '__main__':

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)

    client = google.cloud.logging.Client()
    client.get_default_handler()
    client.setup_logging()

    app.run(host='127.0.0.1', port=8080, debug=DEBUG)
