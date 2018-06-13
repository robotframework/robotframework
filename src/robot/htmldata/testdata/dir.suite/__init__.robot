*** Settings ***
Documentation  Documentation for the whole test suite. All this forms a single
...            paragraph starting from RF 2.7.2. And the paragraph is getting
...            pretty long. And the paragraph is getting pretty long. And the
...            paragraph is getting pretty long. And the paragraph is getting
...            pretty long. Supported formatting is demonstrated below.

...            = Title Level 1 =
...            Text for level 1
...
...            == Title Level 2 ==
...            Text for level 2
...
...            === Title Level 3 ===
...            Text for level 3

...            - *URL:*    http://robotframework.org
...            - _Image:_  http://icons.iconarchive.com/icons/martin-berube/character/48/Robot-icon.png
...            - _*Link:*_ [http://robotframework.org|Robot Framework]
...            - Image link: [http://robotframework.org|http://icons.iconarchive.com/icons/martin-berube/character/48/Robot-icon.png]
...            ----------------------------
...            |           =My=            | = Table = |
...            | http://robotframework.org | _italic_  |
...            | foo |
...            regular line
...            | pre *formatted*
...            | \ \ content\t\with whitespaces
...            ---
...            - first list item has snowman \u2603 and monkey face \U0001F435
...            - second list item
...            \ is continued \
...            using *two* different approaches (``1 + 1 == 2``)
Metadata       URL           http://robotframework.org
Metadata       Image         http://icons.iconarchive.com/icons/martin-berube/character/48/Robot-icon.png
Metadata       Formatting    *Bold* and _italics_ and ``code``
Metadata       </script>     < &lt; </script>
Suite Setup    Log    higher level suite setup
Force Tags     i1    i2
