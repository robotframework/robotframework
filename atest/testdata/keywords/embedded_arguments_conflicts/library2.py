from robot.api.deco import keyword


@keyword('${match} in ${both} libraries')
def match_in_both_libraries(match, both):
    assert match == 'Match'
    assert both == 'both'

@keyword('Follow search ${order} in libraries')
def follow_search_order_in_libraries(order):
    assert order == 'order'

@keyword('${match} libraries')
def match_libraries(match):
    assert False


@keyword('Unresolvable ${conflict} in library')
def unresolvable_conflict_in_library(conflict):
    assert False


@keyword('${possible} conflict in library')
def possible_conflict_in_library(possible):
    assert possible == 'No'
