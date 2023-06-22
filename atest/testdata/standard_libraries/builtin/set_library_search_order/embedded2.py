from robot.api.deco import keyword


@keyword('Get ${Match} With Search Order')
def get_best_match_ever_with_search_order(Match):
    raise AssertionError('Should not be run due to a better match'
                         'in same library.')

@keyword('Get Best ${Match:\w+} With Search Order')
def get_best_match_with_search_order(Match):
    raise AssertionError('Should not be run due to a better match'
                         'in same library.')

@keyword('Get Best ${Match} With Search Order')
def get_best_match_with_search_order(Match):
    assert Match == "Match Ever"
    return "embedded2"
