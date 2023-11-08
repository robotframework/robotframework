def get_variables(name, value='default value', conversion: int = 0):
    if name == 'FAIL':
        1/0
    assert isinstance(conversion, int)
    varz = {name: value,
            'ANOTHER_SCALAR': 'Variable from CLI var file with get_variables',
            'LIST__ANOTHER_LIST': ['List variable from CLI var file',
                                   'with get_variables'],
            'CONVERSION': conversion}
    for name in 'PRIORITIES_1', 'PRIORITIES_2', 'PRIORITIES_2B':
        varz[name] = 'Second Variable File from CLI'
    return varz
