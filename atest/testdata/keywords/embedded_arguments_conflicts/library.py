from robot.api.deco import keyword


@keyword('${x} in library')
def x_in_library(x):
    assert x == 'x'


@keyword('${x} and ${y} in library')
def x_and_y_in_library(x, y):
    assert x == 'x'
    assert y == 'y'


@keyword('${y:y} in library')
def y_in_library(y):
    assert False


@keyword('${match} in ${both} libraries')
def match_in_both_libraries(match, both):
    assert False


@keyword('Best ${match} in ${one of} libraries')
def best_match_in_one_of_libraries(match, one_of):
    assert match == 'match'
    assert one_of == 'one of'

@keyword('Follow search ${disorder} in libraries')
def follow_search_order_in_libraries(disorder):
    assert disorder == 'disorder should not happen'

@keyword('Unresolvable conflict in library')
def unresolvable_conflict_in_library():
    assert False
