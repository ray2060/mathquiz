from flask import request, render_template
from flask.views import MethodView


class APlusBView(MethodView):

    def get(self):
        context = {}
        return render_template('a_plus_b.html', **context)

    def post(self):
        a = int(request.form['a'])
        b = int(request.form['b'])
        context = {
                'flag': True,
                'a': a,
                'b': b,
                'sum': a + b,
            }
        return render_template('a_plus_b.html', **context)
