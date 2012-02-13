from subprocess import call

def test_env_var_in_child_process(var):
    rc = call(['python', '-c', 'import os, sys; sys.exit("%s" in os.environ)' % var])
    if rc !=1 :
        raise AssertionError("Variable '%s' did not exist in child environment" % var)

