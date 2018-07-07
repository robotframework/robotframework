def kw_only_arg(*, kwo):
    return kwo


def many_kw_only_args(*, first, second, third):
    return first + second + third


def kw_only_arg_with_default(*, kwo='default', another='another'):
    return '{}-{}'.format(kwo, another)


def kw_only_arg_with_annotation(*, kwo: str):
    return kwo


def kw_only_arg_with_annotation_and_default(*, kwo: str='default'):
    return kwo
