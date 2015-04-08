from robot.api.deco import keyword


@keyword(name="${a}*lib*${b}")
def mult_match3(a, b):
    print "%s*lib*%s" % (a, b)
