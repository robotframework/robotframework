def A_type_annotation(integer: int, boolean: bool, string: str):
    pass


def B_annotation_as_documentation(argument: 'One of the usages in PEP-3107'):
    pass


def C_annotation_and_default(integer: int=42, list_: list=None):
    pass


def D_annotated_kw_only_args(*, kwo: int, with_default: str='value'):
    pass


def E_annotated_varags_and_kwargs(*varargs: int, **kwargs: "This feels odd..."):
    pass
