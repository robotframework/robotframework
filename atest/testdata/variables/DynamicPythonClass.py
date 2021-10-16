class DynamicPythonClass:

    def get_variables(self, *args):
        return {'dynamic_python_string': ' '.join(args),
                'LIST__dynamic_python_list': args}
