Robot Framework Quick Start Guide
=================================

To view the Quick Start Guide simply open `quickstart.html` into your
favorite browser. That file contains also instructions how to execute
the guide as a demo.

The system under test used in the demo is under `sut` directory along
with its unit tests. The needed test library is located in `testlibs`.

Quick Start Guide itself is created using reStructuredText__ and the
source text is in `quickstart.txt` file. For more information about
reStructuredText and software needed for creating the HTML version of
the guide, see see README file of the User Guide in 
`../userguide/README.txt`.

When all preconditions (docutils and Pygments) are installed, the HTML
version of the guide can be generated with `qs2html.py` script. To see
the available options, just run the script without arguments like::

   python qs2html.py


__reStructuredText: http://docutils.sourceforge.net/rst.html
