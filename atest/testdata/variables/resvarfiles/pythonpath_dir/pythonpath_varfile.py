def get_variables(*args):
    return {
        f"PYTHONPATH VAR {len(args)}": "Varfile found from PYTHONPATH",
        f"PYTHONPATH ARGS {len(args)}": "-".join(args),
    }
