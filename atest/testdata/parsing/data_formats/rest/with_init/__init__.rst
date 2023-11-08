.. code:: robotframework

  ** Settings **
  Suite Setup     Suite Setup
  Documentation   Testing suite init file
  Invalid Init    Setting

  ** Variables **
  ${msg} =  Running suite setup

  ** Keywords **
  Suite Setup      Log      ${msg}     # No more arguments!
