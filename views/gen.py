import random

from flask import request, render_template
from flask.views import MethodView

from helpers import *


class GenView(MethodView):

    def get(self):
        context = {}
        return render_template('gen_form.html', **context)

    def post(self):
        a = int(request.form['a'])
        b = int(request.form['b'])
        context = {
                'flag': True,
                'a': a,
                'b': b,
                'sum': a + b,
            }
        return render_template('gen_result.html', **context)




if __name__ == '__main__':
    print_title('A Simple Math Quiz Generator')

    groups = 0
    tasks = []
    negative = False

    path = sys.argv[0][:sys.argv[0].rfind('\\') + 1]
    cf = f'{path}{CONFIG_FILE}'
    if not os.path.exists(cf):
        sys.exit(f'Configuration file not found: {cf}')
    cp = configparser.ConfigParser()
    try:
        cp.read(cf, encoding='utf-8')
        groups = int(cp.get('SYSTEM', 'GROUPS'))
        for t in cp.get('SYSTEM', 'TASKS').split('|'):
            results = get_choices(cp.get(t, 'TEMPLATES'))
            task = {
                    'num': int(cp.get(t, 'NUM')),
                    'negative': cp.get(t, 'NEGATIVE') in ['YES', 'Y'],
                    'divide_exactly': cp.get(t, 'DIVIDE_EXACTLY') in ['YES', 'Y'],
                    'quotient_zero': cp.get(t, 'QUOTIENT_ZERO') in ['YES', 'Y'],
                    'templates': [cp.get(t, r[0]).strip() for r in results],
                    'weights': [r[1] for r in results],
                    'blank': int(cp.get(t, 'BLANK'))
                }
            tasks.append(task)
    except Exception as e:
        sys.exit(f'Exception in loading {cf}: {e}')

    quizzes = []
    for i in range(groups):
        print_title(f'GROUP {i + 1}')
        o = 0
        for j in range(len(tasks)):
            task = tasks[j]
            for k in range(task['num']):
                template = random.choices(task['templates'], \
                        weights=task['weights'])[0]
                quiz = Quiz(task['negative'], task['divide_exactly'], \
                        task['quotient_zero'])
                quiz.get_quiz(template)
                while quiz in quizzes:
                    quiz.get_quiz(template)
                o += 1
                print(f'{o:2d}.  {quiz}')
                for l in range(task['blank']):
                    print('')
                quizzes.append(quiz)
        print('')
