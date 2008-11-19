def get_variables():
    varz = { 'ANOTHER_SCALAR': 'Variable from CLI var file with get_variables',
             'LIST__ANOTHER_LIST': ['List variable from CLI var file',
                                    'with get_variables'] }
    for name in 'PRIORITIES_1', 'PRIORITIES_2', 'PRIORITIES_2B':
        varz[name] = 'Second Variable File from CLI'
    return varz
