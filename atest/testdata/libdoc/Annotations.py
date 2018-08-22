def A_type_annotation(integer: int, boolean: bool, string: str):
    pass


def B_annotation_and_default(integer: int=42, list_: list=None):
    pass


def C_annotated_kw_only_args(*, kwo: int, with_default: str='value'):
    pass


def D_annotated_varags_and_kwargs(*varargs: int, **kwargs: bool):
    pass


def E_non_type_annotations_are_ignored(arg: 'One of the usages in PEP-3107',
                                       *varargs: 'But surely feels odd...'):
    pass
