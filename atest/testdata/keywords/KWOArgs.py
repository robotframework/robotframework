def kwoarg(*, kwo):
    return kwo


def kwoarg_with_default(*, kwo='default'):
    return kwo


def kwoarg_with_annotation(*, kwo: str):
    return kwo


def kwoarg_with_annotation_and_default(*, kwo: str='default'):
    return kwo
