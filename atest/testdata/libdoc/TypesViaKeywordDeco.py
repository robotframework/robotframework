from robot.api.deco import keyword as _keyword


class UnknownType(object):
    pass


@_keyword(types={'integer': int, 'boolean': bool, 'string': str})
def A_basics(integer, boolean, string):
    pass


@_keyword(types={'integer': int, 'list_': list})
def B_with_defaults(integer=42, list_=None):
    pass


@_keyword(types={'varargs': int, 'kwargs': bool})
def C_varags_and_kwargs(*varargs, **kwargs):
    pass


@_keyword(types={'unknown': UnknownType, 'unrecognized': Ellipsis})
def D_unknown_types(unknown, unrecognized):
    pass


@_keyword(types={'arg': 'One of the usages in PEP-3107',
                'varargs': 'But surely feels odd...'})
def E_non_type_annotations(arg, *varargs):
    pass


try:
    exec('''
@_keyword(types={'kwo': int, 'with_default': str})
def F_kw_only_args(*, kwo, with_default='value'):
    pass
''')
except SyntaxError:
    pass
