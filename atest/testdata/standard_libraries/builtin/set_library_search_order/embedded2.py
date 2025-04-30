from robot.api.deco import keyword


@keyword("Get ${Match} With Search Order")
def get_best_match_ever_with_search_order_1(match):
    raise AssertionError("Should not be run due to a better matchin same library.")


@keyword("Get Best ${Match:\w+} With Search Order")
def get_best_match_with_search_order_2(match):
    raise AssertionError("Should not be run due to a better matchin same library.")


@keyword("Get Best ${Match} With Search Order")
def get_best_match_with_search_order_3(match):
    assert match == "Match Ever"
    return "embedded2"
