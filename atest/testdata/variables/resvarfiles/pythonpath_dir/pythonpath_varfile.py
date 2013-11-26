def get_variables(*args):
    return {'PYTHONPATH VAR %d' % len(args): 'Varfile found from PYTHONPATH',
            'PYTHONPATH ARGS %d' % len(args): '-'.join(args)}
