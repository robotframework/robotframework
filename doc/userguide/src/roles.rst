.. Roles are used like :role:`example` or via aliases. Styled in userguide.css.

   Standard reST roles
   -------------------

   Standard roles are used as much as possible. There are others but these
   make most sense in our context. For more information see
   http://docutils.sourceforge.net/docs/ref/rst/roles.html

   code       Code, CLI examples, GUI entries, variables, etc. Alias `example`
              configured below.
   literal    Program and environment variable names (e.g. :literel:`rebot`).
              Alias ``example``.
   emphasis   In practice italics. Used with some terms. Alias *example*.
   strong     In practice bold. Alias **example**.

   Sphinx roles
   ------------

   Need to be defined here but using these eases migrating to Sphinx in the
   future. For details see http://sphinx-doc.org/markup/inline.html

   option     Command line options. Notice that examples should use code role.
              Notice also that standard reST uses option class in option lists.
   file       File and directory paths.

   Custom roles
   ------------

   Our own custom rules.

   setting    Setting names (e.g. :setting:`Library`, :setting:`[Setup]`).
   name       Keyword, library, test case and test suite names
   codesc     Formatted like standard code role but supports escaping.
              For example, output of :codesc:`\`example\`` is `example`, not
              \`example\`.

.. default-role:: code
.. role:: option
.. role:: file
.. role:: setting
.. role:: name
.. role:: codesc
