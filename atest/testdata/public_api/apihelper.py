import os


def verify_suites(suite, path_to_data):
    suites = [ suite ] + suite.suites
    return verify_attributes(suites, parse_data(path_to_data))

def verify_tests(suite, path_to_data):
    tests = _get_tests(suite)
    return verify_attributes(tests, parse_data(path_to_data))
    
def _get_tests(suite):
    tests = []
    for suite in suite.suites:
        tests.extend(suite.tests)
    return tests


def verify_attributes(items, data):
    fails = 0
    for i in range(len(data[0])-2):
        suite = test = items[i]
        for attr in data:
            expected =  attr['EXP%d' % (i+1)]
            if expected == 'N/A':
                continue
            actual = eval(attr['ACTUAL'])
            
            try:
                expected = eval(expected)
            except:
                pass
            fails += verify_attribute(attr['TITLE'], actual, expected )
    return fails
    

def verify_attribute(name, actual, expected):
    title = '%s: %s' % (name, actual)
    if actual == expected:
        print '%s | PASS |' % title.ljust(70)
        return 0
    else:
        print '%s | FAIL |' % title.ljust(70)
        print '  Expected: %s' % expected, "(types: %s, %s" % (type(actual), type(expected))
        return 1
    
def parse_data(path):
    content = open(path).read().splitlines()
    data = []
    for row in content:
        if row.strip() == '' or row.startswith('#'):
            continue
        cells = [ cell.strip() for cell in row.split('|') ]
        titles = [ 'TITLE', 'ACTUAL' ] + [ 'EXP%d' % (i+1) for i in range(len(cells[2:]))]
        if cells[0] == '...':
            for title, cell in zip(titles[2:], cells[2:]):
                if cell != '':
                    data[-1][title] += '\n' + cell
            continue
        data.append(dict(zip(titles, cells)))
    return data

    
if __name__ == '__main__':
#    _verify_attribute('title', 'foo', 'foo')
#    _verify_attribute('false_title', 'bar', 'foo')
#    _verify_attribute('name', 'value in \nmutltiple lines','value in \nmutltiple lines')
    parse_data('data.txt')