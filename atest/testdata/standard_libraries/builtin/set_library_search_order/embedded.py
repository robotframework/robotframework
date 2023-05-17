from robot.api.deco import keyword


@keyword('No ${Ope}ration')
def no_operation(ope):
    raise AssertionError('Should not be run due to keywords with normal '
                         'arguments having higher precedence.')


@keyword('Get ${Name}')
def get_name(name):
    raise AssertionError('Should not be run due to keywords with normal '
                         'arguments having higher precedence.')

@keyword('Get ${Name} With Search Order')
def get_name_with_search_order(name):
    return "embedded"
