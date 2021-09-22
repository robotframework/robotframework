import sys


def print_one_html_line():
    print('*HTML* <a href="http://www.google.com">Google</a>')


def print_many_html_lines():
    print('*HTML* <table border=1>\n<tr><td>0,0</td><td>0,1</td></tr>')
    print('<tr><td>1,0</td><td>1,1</td></tr>\n</table>')
    print('*HTML*This is html <hr>')
    print('*INFO*This is not html <br>')


def print_html_to_stderr():
    print('*HTML* <i>Hello, stderr!!</i>', file=sys.stderr)


def print_with_all_levels():
    for level in 'TRACE DEBUG INFO HTML WARN ERROR'.split():
        print('*%s* %s message' % (level, level.title()))
