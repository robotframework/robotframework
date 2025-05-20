from subprocess import call


def test_env_var_in_child_process(var):
    rc = call(["python", "-c", f"import os, sys; sys.exit('{var}' in os.environ)"])
    if rc != 1:
        raise AssertionError(f"Variable '{var}' did not exist in child environment")
