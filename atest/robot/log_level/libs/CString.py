#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# -- import standard Python modules
import os, ntpath, platform, re

class CString(object):
   """
The class ``CString`` contains some string computation methods like e.g. normalizing a path.
   """

   def NormalizePath(sPath=None, bWin=False, sReferencePathAbs=None, bConsiderBlanks=False, bExpandEnvVars=True, bMask=True):
      """
Normalizes local paths, paths to local network resources and internet addresses

**Arguments:**

* ``sPath``

  / *Condition*: required / *Type*: str /

  The path to be normalized. Paths can start with environment variables. Accepted are notations for both Windows
  (``%ENVVAR%``) and Linux (``${ENVVAR}``). Under Windows also the Linux notation will be resolved.

* ``bWin``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True`` then returned path contains masked backslashes as separator, otherwise slashes

* ``sReferencePathAbs``

  / *Condition*: optional / *Type*: str / *Default*: None /

  In case of ``sPath`` is relative and ``sReferencePathAbs`` (expected to be absolute) is given, then
  the returned absolute path is a join of both input paths

* ``bConsiderBlanks``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True`` then the returned path is encapsulated in quotes - in case of the path contains blanks

* ``bExpandEnvVars``

  / *Condition*: optional / *Type*: bool / *Default*: True /

   If ``True`` then in the returned path environment variables are resolved, otherwise not.

* ``bMask``

  / *Condition*: optional / *Type*: bool / *Default*: True (requires ``bWin=True``)/

  * If ``bWin`` is ``True`` and ``bMask`` is ``True`` then the returned path contains masked backslashes as separator.
  * If ``bWin`` is ``True`` and ``bMask`` is ``False`` then the returned path contains single backslashes only - this might be
    required for applications, that are not able to handle masked backslashes.
  * In case of ``bWin`` is ``False`` ``bMask`` has no effect.

**Returns:**

* ``sPath``

  / *Type*: str /

  The normalized path (is ``None`` in case of ``sPath`` is ``None``)
      """

      if sPath is not None:

         # - remove leading and trailing horizontal space
         sPath = sPath.strip(" \t\r\n")

         # - remove leading and trailing quotes
         sPath = sPath.strip("\"'")

         # - remove once more leading and trailing horizontal space
         #   (after the removal of leading and trailing quotes further horizontal space might be there, that has to be removed;
         #    but further levels of nesting are not considered)
         sPath = sPath.strip(" \t")

         if sPath == "":
            return sPath

         # - remove trailing slash or backslash (maybe at end of path to folder)
         sPath = sPath.rstrip("/\\")

         # -- expand environment variables
         if bExpandEnvVars is True:
            sPattern_envvar = r"^\$\{(\w+?)\}" # check for Linux notation (shall be usable also under Windows)
            regex_envvar    = re.compile(sPattern_envvar)
            sPlatformSystem = platform.system()
            sPathModified = sPath
            for sEnvVar in regex_envvar.findall(sPath):
               sSearch = "${" + sEnvVar + "}"
               if sPlatformSystem == "Windows":
                  sReplace = "%" + sEnvVar + "%"
                  sPathModified = sPathModified.replace(sSearch, sReplace)
            # eof for sEnvVar in regex_envvar.findall(sPath):
            sPath = os.path.expandvars(sPathModified)

         # --------------------------------------------------------------------------------------------------------------
         # consider internet addresses and local network resources
         # --------------------------------------------------------------------------------------------------------------
         # -- local network resource / file server
         #    (prepare for Windows explorer)
         # either (default)
         # //server.com/abc/xyz
         # or (with bWin=True); bMask must be False because \\server.com\\abc\\xyz is not allowed
         # \\server.com\abc\xyz
         # (=> user is allowed to select bWin but not bMask)
         #
         # -- local network resource / file server
         #    (prepare for web browser)
         # after 'file://///' only single slashes allowed; bWin and bMask must be False
         # file://///server.com/abc/xyz
         # (=> user is NOT allowed to select bWin and bMask)
         #
         # -- internet address
         # after server name only single slashes allowed; bWin and bMask must be False
         # http://server.com/abc/xyz
         # https://server.com/abc/xyz
         # (=> user is NOT allowed to select bWin and bMask)
         #
         # - not allowed (=> this method must not return this format):
         # http:\\server.com
         # https:\\server.com
         # --------------------------------------------------------------------------------------------------------------

         sPathPrefix = None

         # In case there is any prefix, we remove this prefix, we compute the remaining part of the path separately,
         # we also modify this prefix manually, and at the end we put the new prefix back to the path.

         if ( (sPath[:2] == "\\\\") or (sPath[:2] == "//") ):
            sPath = sPath[2:]
            if bWin is True:
               sPathPrefix = "\\\\"
            else:
               sPathPrefix = "//"
            bMask = False # !!! this overrules the input parameter value, because masked backslashes are not allowed in remaining path !!!
         elif sPath[:10] == "file://///": # exactly this must be given; all other combinations of slashes and backslashes are not handled
            sPath = sPath[10:]
            sPathPrefix = "file://///"
            bWin  = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
            bMask = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
         elif ( (sPath[:7] == "http://") or (sPath[:7] == "http:\\\\") ):
            sPath = sPath[7:]
            sPathPrefix = "http://"
            bWin  = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
            bMask = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
         elif ( (sPath[:8] == "https://") or (sPath[:8] == "https:\\\\") ):
            sPath = sPath[8:]
            sPathPrefix = "https://"
            bWin  = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
            bMask = False # !!! this overrules the input parameter value, because only single slashes allowed in remaining path !!!
         else:
            # Internet addresses and local network resources handled, now checking for relative paths:
            # In case of sPath is a relative path AND an absolute reference path is provided
            # merge them to an absolute path; without reference path use standard function to
            # convert relative path to absolute path
            if ( (sPath[0] != "%") and (sPath[0] != "$") ):
               # If sPath starts with '%' or with '$' it is assumed that the path starts with an environment variable (Windows or Linux).
               # But in this case 'os.path.isabs(sPath)' will not detect this to be an absolute path and will call
               # 'sPath = os.path.abspath(sPath)' (depending on sReferencePathAbs). This will accidently merge
               # the root path together with the path starting with the environment variable and cause invalid results.
               if os.path.isabs(sPath) is False:
                  if sReferencePathAbs is not None:
                     sPath = os.path.join(sReferencePathAbs, sPath)
                  else:
                     sPath = os.path.abspath(sPath)

         # eof computation of sPathPrefix

         # - normalize the path (collapse redundant separators and up-level references)
         #   on Windows this converts slashes to backward slashes
         # sPath = os.path.normpath(sPath) # under Linux this unfortunately keeps redundant separators (in opposite to Windows)
         # -- alternative
         sPath = ntpath.normpath(sPath)

         # - exchange single backslashes by single slashes (= partly we have to repair the outcome of normpath)
         if bWin is False:
            sPath = sPath.replace("\\", "/")
         else:
            if bMask is True:
               sPath = sPath.replace("\\", "\\\\")

         # - restore the path prefix
         if sPathPrefix is not None:
            sPath = f"{sPathPrefix}{sPath}"

         # - consider blanks (prepare path for usage in Windows command line)
         if bConsiderBlanks is True:
            if sPath.find(" ") >= 0:
               sPath = f"\"{sPath}\""

      # eof if sPath is not None:

      return sPath

   # eof NormalizePath(sPath=None, bWin=False, sReferencePathAbs=None, bConsiderBlanks=False, bExpandEnvVars=True, bMask=True)

   def StringFilter(sString           = None,
                    bCaseSensitive    = True,
                    bSkipBlankStrings = True,
                    sComment          = None,
                    sStartsWith       = None,
                    sEndsWith         = None,
                    sStartsNotWith    = None,
                    sEndsNotWith      = None,
                    sContains         = None,
                    sContainsNot      = None,
                    sInclRegEx        = None,
                    sExclRegEx        = None,
                    bDebug            = False):
      """
This method provides a bunch of predefined filters that can be used singly or combined to come to a final conclusion if the string fulfils all criteria or not.

These filters can be e.g. used to select or exclude lines while reading from a text file. Or they can be used to select or exclude files or folders
while walking through the file system.

**The following filters are available:**

**bSkipBlankStrings**

   * Leading and trailing spaces are removed from the input string at the beginning
   * In case of the result is an empty string and ``bSkipBlankStrings`` is ``True``, the method immediately returns ``False``
     and all other filters are ignored

**sComment**

   * In case of the input string starts with the string ``sComment``, the method immediately returns ``False``
     and all other filters are ignored
   * Leading blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * The idea behind this decision is: Ignore a string that is commented out

**sStartsWith**

   * The criterion of this filter is fulfilled in case of the input string starts with the string ``sStartsWith``
   * Leading blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``OR``)

**sEndsWith**

   * The criterion of this filter is fulfilled in case of the input string ends with the string ``sEndsWith``
   * Trailing blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``OR``)

**sStartsNotWith**

   * The criterion of this filter is fulfilled in case of the input string does **not** start with the string ``sStartsNotWith``
   * Leading blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``AND``)

**sEndsNotWith**

   * The criterion of this filter is fulfilled in case of the input string does **not** end with the string ``sEndsNotWith``
   * Trailing blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``AND``)

**sContains**

   * The criterion of this filter is fulfilled in case of the input string contains the string ``sContains`` at any position
   * Leading and trailing blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``OR``)

**sContainsNot**

   * The criterion of this filter is fulfilled in case of the input string does **not** contain the string ``sContainsNot`` at any position
   * Leading and trailing blanks within the input string have no effect
   * The decision also depends on ``bCaseSensitive``
   * More than one string can be provided (semicolon separated; logical join: ``AND``)

**sInclRegEx**

   * *Include* filter based on regular expressions (consider the syntax of regular expressions!)
   * The criterion of this filter is fulfilled in case of the regular expression ``sInclRegEx`` matches the input string
   * Leading and trailing blanks within the input string are considered
   * ``bCaseSensitive`` has no effect
   * A semicolon separated list of several regular expressions is **not** supported

**sExclRegEx**

   * *Exclude* filter based on regular expressions (consider the syntax of regular expressions!)
   * The criterion of this filter is fulfilled in case of the regular expression ``sExclRegEx`` does **not** match the input string
   * Leading and trailing blanks within the input string are considered
   * ``bCaseSensitive`` has no effect
   * A semicolon separated list of several regular expressions is **not** supported

**Further arguments:**

* ``sString``

  / *Condition*: required / *Type*: str /

  The input string that has to be investigated.

* ``bCaseSensitive``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  If ``True``, the standard filters work case sensitive, otherwise not.

* ``bDebug``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True``, additional output is printed to console (e.g. the decision of every single filter), otherwise not.

**Returns:**

* ``bAck``

  / *Type*: bool /

  Final statement about the input string ``sString`` after filter computation

Further details together with codde examples can be found within chapter **Description**, subsubsection **StringFilter**.
      """

      if sString is None:
         return False # hard coded here; no separate filter for that decision

      # The original string 'sString' is used by regular expression filters sInclRegEx and sExclRegEx.
      # The stripped string 'sStringStripped' is used by all other filters.
      sStringStripped = sString.strip(" \t\r\n")

      # -- skipping blank strings or strings commented out; other filters will not be considered any more in this case

      if bSkipBlankStrings is True:
         if sStringStripped == "":
            return False

      if sComment is not None:
         if sComment != "":
            if bCaseSensitive is True:
              if sStringStripped.startswith(sComment) is True:
                 return False
            else:
              if sStringStripped.upper().startswith(sComment.upper()) is True:
                 return False

      # -- consider further filters
      #
      # No filter set (= no criteria defined) => use this string (bAck is True).
      #
      # At least one filter set (except sExclRegEx), at least one set filter fits (except sExclRegEx) => use this string.
      # Filter sExclRegEx is set and fits => skip this string (final veto).
      # At least one filter does not fit (except sExclRegEx) => skip this string.
      #
      # All filters (except sExclRegEx) are include filter (bAck is True in case of all set filters fit, also the 'not' filters)
      # The filter sExclRegEx is an exclude filter and has final veto right (can revoke the True from other filters).
      #
      # All filters (except sInclRegEx and sExclRegEx) are handled as 'raw strings': no wild cards, just strings, considering bCaseSensitive.
      # The filters sInclRegEx and sExclRegEx are handled as regular expressions; bCaseSensitive is not considered here.

      # -- filter specific flags (containing the names of the criteria within their names)
      bStartsWith    = None
      bEndsWith      = None
      bStartsNotWith = None
      bEndsNotWith   = None
      bContains      = None
      bContainsNot   = None
      bInclRegEx     = None
      bExclRegEx     = None

      # Meaning:
      # - Flag is None : filter not set => filter has no effect
      # - Flag is True : filter set => result: use the input string (from this single filter flag point of view)
      # - Flag is False: filter set => result: do not use the input string (from this single filter flag point of view)
      # The results of all flags will be merged at the end of this function to one final conclusion to use the input string
      # (bAck is True) or not (bAck is False).
      # Logical join between all set filters: AND

      # substitute for the masked filter separator '\n' (hopefully the input string does not contain this substitute)
      sSeparatorSubstitute = "#|S#|E#|P#|A#|R#|A#|T#|O#|R#"

      # -- filter: starts with
      #    > several filter strings possible (separated by semicolon; logical join: OR)
      if sStartsWith is not None:
         if sStartsWith != "":
            sStartsWithModified = sStartsWith.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listStartsWith = []
            if sStartsWith.find(";") >= 0:
               listParts = sStartsWithModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listStartsWith.append(sPart)
            else:
               sStartsWithModified = sStartsWith.replace(r"\;", ";") # convert to unmasked version
               listStartsWith.append(sStartsWithModified)

            bStartsWith = False
            for sStartsWith in listStartsWith:
               if bCaseSensitive is True:
                  if sStringStripped.startswith(sStartsWith) is True:
                     bStartsWith = True
                     break
               else:
                  if sStringStripped.upper().startswith(sStartsWith.upper()) is True:
                     bStartsWith = True
                     break

      # -- filter: ends with
      #    > several filter strings possible (separated by semicolon; logical join: OR)
      if sEndsWith is not None:
         if sEndsWith != "":
            sEndsWithModified = sEndsWith.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listEndsWith = []
            if sEndsWith.find(";") >= 0:
               listParts = sEndsWithModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listEndsWith.append(sPart)
            else:
               sEndsWithModified = sEndsWith.replace(r"\;", ";") # convert to unmasked version
               listEndsWith.append(sEndsWithModified)

            bEndsWith = False
            for sEndsWith in listEndsWith:
               if bCaseSensitive is True:
                  if sStringStripped.endswith(sEndsWith) is True:
                     bEndsWith = True
                     break
               else:
                  if sStringStripped.upper().endswith(sEndsWith.upper()) is True:
                     bEndsWith = True
                     break

      # -- filter: starts not with
      #    > several filter strings possible (separated by semicolon; logical join: AND)
      if sStartsNotWith is not None:
         if sStartsNotWith != "":
            sStartsNotWithModified = sStartsNotWith.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listStartsNotWith = []
            if sStartsNotWith.find(";") >= 0:
               listParts = sStartsNotWithModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listStartsNotWith.append(sPart)
            else:
               sStartsNotWithModified = sStartsNotWith.replace(r"\;", ";") # convert to unmasked version
               listStartsNotWith.append(sStartsNotWithModified)

            bStartsNotWith = True
            for sStartsNotWith in listStartsNotWith:
               if bCaseSensitive is True:
                  if sStringStripped.startswith(sStartsNotWith) is True:
                     bStartsNotWith = False
                     break
               else:
                  if sStringStripped.upper().startswith(sStartsNotWith.upper()) is True:
                     bStartsNotWith = False
                     break

      # -- filter: ends not with
      #    > several filter strings possible (separated by semicolon; logical join: AND)
      if sEndsNotWith is not None:
         if sEndsNotWith != "":
            sEndsNotWithModified = sEndsNotWith.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listEndsNotWith = []
            if sEndsNotWith.find(";") >= 0:
               listParts = sEndsNotWithModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listEndsNotWith.append(sPart)
            else:
               sEndsNotWithModified = sEndsNotWith.replace(r"\;", ";") # convert to unmasked version
               listEndsNotWith.append(sEndsNotWithModified)

            bEndsNotWith = True
            for sEndsNotWith in listEndsNotWith:
               if bCaseSensitive is True:
                  if sStringStripped.endswith(sEndsNotWith) is True:
                     bEndsNotWith = False
                     break
               else:
                  if sStringStripped.upper().endswith(sEndsNotWith.upper()) is True:
                     bEndsNotWith = False
                     break

      # -- filter: contains
      #    > several filter strings possible (separated by semicolon; logical join: OR)
      if sContains is not None:
         if sContains != "":
            sContainsModified = sContains.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listContains = []
            if sContainsModified.find(";") >= 0:
               listParts = sContainsModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listContains.append(sPart)
            else:
               sContainsModified = sContains.replace(r"\;", ";") # convert to unmasked version
               listContains.append(sContainsModified)

            bContains = False
            for sContains in listContains:
               if bCaseSensitive is True:
                  if sStringStripped.find(sContains) >= 0:
                     bContains = True
                     break
               else:
                  if sStringStripped.upper().find(sContains.upper()) >= 0:
                     bContains = True
                     break

      # -- filter: contains not
      #    > several filter strings possible (separated by semicolon; logical join: AND)
      if sContainsNot is not None:
         if sContainsNot != "":
            sContainsNotModified = sContainsNot.replace(r"\;", sSeparatorSubstitute) # replace the masked separator by a substitute separator
            listContainsNot = []
            if sContainsNot.find(";") >= 0:
               listParts = sContainsNotModified.split(";")
               for sPart in listParts:
                  sPart = sPart.replace(sSeparatorSubstitute , ";") # recover the original version
                  listContainsNot.append(sPart)
            else:
               sContainsNotModified = sContainsNot.replace(r"\;", ";") # convert to unmasked version
               listContainsNot.append(sContainsNotModified)

            bContainsNot = True
            for sContainsNot in listContainsNot:
               if bCaseSensitive is True:
                  if sStringStripped.find(sContainsNot) >= 0:
                     bContainsNot = False
                     break
               else:
                  if sStringStripped.upper().find(sContainsNot.upper()) >= 0:
                     bContainsNot = False
                     break

      # -- filter: sInclRegEx
      #    > (take care to mask special characters that are part of the syntax of regular expressions!)
      #    > bCaseSensitive not considered here
      if sInclRegEx is not None:
         if sInclRegEx != "":
            bInclRegEx = False
            if re.search(sInclRegEx, sString) is not None:
               bInclRegEx = True

      # -- last filter: sExclRegEx (final veto right)
      #    > (take care to mask special characters that are part of the syntax of regular expressions!)
      #    > bCaseSensitive not considered here
      if sExclRegEx is not None:
         if sExclRegEx != "":
            bExclRegEx = True
            if re.search(sExclRegEx, sString) is not None:
               bExclRegEx = False

      # -- debug info
      if bDebug is True:
         print("\n* [sString] : '" + str(sString) + "'\n")
         print("  -> [bStartsWith]    : '" + str(bStartsWith)    + "'")
         print("  -> [bEndsWith]      : '" + str(bEndsWith)      + "'")
         print("  -> [bStartsNotWith] : '" + str(bStartsNotWith) + "'")
         print("  -> [bEndsNotWith]   : '" + str(bEndsNotWith)   + "'")
         print("  -> [bContains]      : '" + str(bContains)      + "'")
         print("  -> [bContainsNot]   : '" + str(bContainsNot)   + "'")
         print("  -> [bInclRegEx]     : '" + str(bInclRegEx)     + "'")
         print("  -> [bExclRegEx]     : '" + str(bExclRegEx)     + "'\n")

      # -- final conclusion (AND condition between filters)

      listDecisions = []
      listDecisions.append(bStartsWith)
      listDecisions.append(bEndsWith)
      listDecisions.append(bStartsNotWith)
      listDecisions.append(bEndsNotWith)
      listDecisions.append(bContains)
      listDecisions.append(bContainsNot)
      listDecisions.append(bInclRegEx)
      listDecisions.append(bExclRegEx)

      bAck = False # initial

      # -- 1.) no filter set (all None)
      nCntDecisions = 0
      for bDecision in listDecisions:
         if bDecision is None:
            nCntDecisions = nCntDecisions + 1
      if nCntDecisions == len(listDecisions):
         bAck = True
         if bDebug is True:
            print("     > case [1] - bAck: " + str(bAck))

      # -- 2.) final veto from exclude filter
      if bExclRegEx is False:
         bAck = False
         if bDebug is True:
            print("     > case [2] - bAck: " + str(bAck))

      # -- 3.) exclude filter not set; decision only made by other filters (include)
      if bExclRegEx is None:
         bAck = True
         for bDecision in listDecisions:
            if bDecision is False:
               bAck = False
               break
         if bDebug is True:
            print("     > case [3] - bAck: " + str(bAck))

      # -- 4.) exclude filter is True (only relevant in case of all other filters are not set; otherwise decision only made by other filters (include))
      if bExclRegEx is True:
         if ( (bStartsWith is None) and
              (bEndsWith is None) and
              (bStartsNotWith is None) and
              (bEndsNotWith is None) and
              (bContains is None) and
              (bContainsNot is None) and
              (bInclRegEx is None) ):
            bAck = True
            if bDebug is True:
               print("     > case [4.1] - bAck: " + str(bAck))
         else:
            bAck = True
            for bDecision in listDecisions:
               if bDecision is False:
                  bAck = False
                  break
            if bDebug is True:
               print("     > case [4.2] - bAck: " + str(bAck))

      if bDebug is True:
         print()

      return bAck

   # eof def StringFilter(...)

   def FormatResult(sMethod="", bSuccess=True, sResult=""):
      """
Formats the result string ``sResult`` depending on ``bSuccess``:

* ``bSuccess`` is ``True`` indicates *success*
* ``bSuccess`` is ``False`` indicates an *error*
* ``bSuccess`` is ``None`` indicates an *exception*

Additionally the name of the method that causes the result, can be provided (*optional*).
This is useful for debugging.

**Arguments:**

* ``sMethod``

  / *Condition*: optional / *Type*: str / *Default*: (empty string) /

  Name of the method that causes the result.

* ``bSuccess``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  Indicates if the computation of the method ``sMethod`` was successful or not.

* ``sResult``

  / *Condition*: optional / *Type*: str / *Default*: (empty string) /

  The result of the computation of the method ``sMethod``.

**Returns:**

* ``sResult``

  / *Type*: str /

  The formatted result string.
      """

      if sMethod is None:
         sMethod = str(sMethod)
      if sResult is None:
         sResult = str(sResult)
      if bSuccess is True:
         if sMethod != "":
            sResult = f"[{sMethod}] : {sResult}"
      elif bSuccess is False:
         sError = "!!! ERROR !!!"
         if sMethod != "":
            sResult = f"{sError}\n[{sMethod}] : {sResult}"
         else:
            sResult = f"{sError}\n{sResult}"
      else:
         sException = "!!! EXCEPTION !!!"
         if sMethod != "":
            sResult = f"{sException}\n[{sMethod}] : {sResult}"
         else:
            sResult = f"{sException}\n{sResult}"
      return sResult

   # eof def FormatResult(sMethod="", bSuccess=True, sResult=""):

   # - make the methods static

   NormalizePath = staticmethod(NormalizePath)
   StringFilter  = staticmethod(StringFilter)
   FormatResult  = staticmethod(FormatResult)

# eof class CString(object):
