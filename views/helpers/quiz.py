import re
import random


def get_choices(s):
    ret = []
    for c in s.split('|'):
        if c.find(':') > -1:
            ret.append((c[:c.find(':')], int(c[c.find(':') + 1:])))
        else:
            ret.append((c, 100))
    return ret


class Quiz():

    def __init__(self, negative=False, divide_exactly=False, \
            quotient_zero=False):
        self.negative = negative
        self.divide_exactly = divide_exactly
        self.quotient_zero = quotient_zero
        self.exp = ''
        self.result = None


    def __str__(self):
        ret = self.exp
        ret = ret.replace('*', '×')
        ret = ret.replace('/', '÷')
        return ret


    def get_quiz(self, template):
        e = ''
        while True:
            e = self._choose(template)
            e = self._assign(e)
            if not self._is_ill(e):
                break
        self.exp = e


    def _choose(self, template):
        template = template.replace('(', '( ')
        template = template.replace(')', ' )')
        ls = []
        for t in template.split():
            results = get_choices(t)
            ls.append(random.choices([r[0] for r in results], \
                    weights = [r[1] for r in results])[0])
        ret = ' '.join(ls)
        ret = ret.replace('( ', '(')
        ret = ret.replace(' )', ')')
        return ret


    def _assign(self, template):
        ret = template
        p = re.compile(r'D(\d+)')
        m = p.search(ret)
        while m:
            rand = self._get_rand(int(m.group(1)))
            ret = p.sub(str(rand), ret, 1)
            m = p.search(ret)
        return ret


    def _is_ill(self, e):
        while ('+' in e) or \
                ('-' in e) or \
                ('*' in e) or \
                ('/' in e):
            e, ill = self._compute_one_step(e)
            if ill:
                return True
        return False


    def _compute_one_step(self, e):
        part = e
        p = re.compile(r'\(([\d+\-*/ ]+)\)')
        m = p.search(part)
        if m:
            part = m.group(1)
        p = re.compile(r'\d+ [*/] \d+')
        m = p.search(part)
        if m:
            part = m.group(0)
        else:
            p = re.compile(r'\d+ [+\-] \d+')
            m = p.search(part)
            if m:
                part = m.group(0)
        try:
            self.result = eval(part)
        except:
            # division by zero
            return '', True
        if (not self.negative) and (self.result < 0):
            return '', True
        if (self.divide_exactly) and (self.result != int(self.result)):
            return '', True
        if (not self.quotient_zero) and ('/' in part) and (self.result < 1):
            return '', True
        e = p.sub(str(int(self.result)), e, 1)
        # remove brackets
        p = re.compile(r'\((\d+)\)')
        m = p.search(e)
        if m:
            e = p.sub(m.group(1), e, 1)
        return e, False


    def _get_rand(self, digits):
        return random.randrange(10 ** (digits - 1), 10 ** digits)
