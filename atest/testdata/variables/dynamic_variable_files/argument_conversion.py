def get_variables(string: str, number: 'int|float'):
    assert isinstance(string, str)
    assert isinstance(number, (int, float))
    return {'string': string, 'number': number}
