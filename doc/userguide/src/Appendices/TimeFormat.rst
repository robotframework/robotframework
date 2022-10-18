Time format
===========

Robot Framework has its own time format that is both flexible to use and easy
to understand. It is used by several keywords (for example, BuiltIn_ keywords
:name:`Sleep` and :name:`Wait Until Keyword Succeeds`), DateTime_ library, and
`timeouts`_.

.. contents::
   :depth: 2
   :local:

Time as number
--------------

The time can always be given as a plain number, in which case it is
interpreted to be seconds. Both integers and floating point numbers
work, and it is possible to use either real numbers or strings
containing numerical values.

.. note:: In some contexts plain numbers can be interpreted otherwise as
          times. For example, with `WHILE loop limit`__ integers denote
          the maximum iteration count.

__ `Limiting WHILE loop iterations`_

Time as time string
-------------------

Representing the time as a time string means using a format such as
`2 minutes 42 seconds`, which is normally easier to understand than
just having the value as seconds. It is, for example, not so easy to
understand how long a time `4200` is in seconds, but
`1 hour 10 minutes` is clear immediately.

The basic idea of this format is having first a number and then a text
specifying what time that number represents. Numbers can be either
integers or floating point numbers, the whole format is case and space
insensitive, and it is possible to add `-` prefix to specify negative
times. The available time specifiers are:

* days, day, d
* hours, hour, h
* minutes, minute, mins, min, m
* seconds, second, secs, sec, s
* milliseconds, millisecond, millis, ms
* microseconds, microsecond, us, μs
* nanoseconds, nanosecond, ns

Examples::

   1 min 30 secs
   1.5 minutes
   90 s
   1 day 2 hours 3 minutes 4 seconds 5 milliseconds 6 microseconds 7 nanoseconds
   1d 2h 3m 4s 5ms 6μs 7 ns
   - 10 seconds

.. note:: Support for micro and nanoseconds is new in Robot Framework 6.0.

Time as "timer" string
----------------------

Time can also be given in timer like
format `hh:mm:ss.mil`. In this format  both hour and millisecond parts
are optional, leading and trailing zeros can be left out when they are not
meaningful, and negative times can be represented by adding the `-`
prefix. For example, following timer and time string values are identical:

.. table:: Timer and time string examples
   :class: tabular

   ============  ======================================
      Timer                   Time string
   ============  ======================================
   00:00:01      1 second
   01:02:03      1 hour 2 minutes 3 seconds
   1:00:00       1 hour
   100:00:00     100 hours
   00:02         2 seconds
   42:00         42 minutes
   00:01:02.003  1 minute 2 seconds 3 milliseconds
   00:01.5       1.5 seconds
   -01:02.345    \- 1 minute 2 seconds 345 milliseconds
   ============  ======================================
