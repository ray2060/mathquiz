from flask import render_template
from flask.views import MethodView


class IndexView(MethodView):

    def get(self):
        context = {}
        return render_template('index.html', **context)
