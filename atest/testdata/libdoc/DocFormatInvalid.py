from DocFormat import DocFormat


class DocFormatInvalid(DocFormat):
    ROBOT_LIBRARY_DOC_FORMAT = 'invalid'


DocFormatInvalid.__doc__ = DocFormat.__doc__
