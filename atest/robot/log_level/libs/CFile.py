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
import os, shutil, platform

# -- import own Python modules
from CString import CString

class enFileStatiType:
   """
The class ``enFileStatiType`` defines the sollowing file states:

* ``closed``
* ``openedforwriting``
* ``openedforappending``
* ``openedforreading``
   """
   closed             = "closed"
   openedforwriting   = "openedforwriting"
   openedforappending = "openedforappending"
   openedforreading   = "openedforreading"

class CFile(object):
   """
The class ``CFile`` provides a small set of file functions with extended parametrization (like switches
defining if a file is allowed to be overwritten or not).

Most of the functions at least returns ``bSuccess`` and ``sResult``.

* ``bSuccess`` is ``True`` in case of no error occurred.
* ``bSuccess`` is ``False`` in case of an error occurred.
* ``bSuccess`` is ``None`` in case of a very fatal error occurred (exceptions).

* ``sResult`` contains details about what happens during computation.

Every instance of CFile handles one single file only and forces exclusive access to this file.

It is not possible to create an instance of this class with a file that is already in use by another instance.

It is also not possible to use ``CopyTo`` or ``MoveTo`` to overwrite files that are already in use by another instance.
This makes the file handling more save against access violations.
   """

   def __init__(self, sFile=None):
      self.__sFile            = CString.NormalizePath(sFile)
      self.__oFileHandle      = None
      self.__oFileStatus      = enFileStatiType.closed
      self.__sLastDestination = None

      try:
         CFile.__listFilesInUse
      except:
         CFile.__listFilesInUse = []

      # exclusive access is required (checked by self.__bIsFreeToUse; relevant for destination in CopyTo and MoveTo)
      if self.__sFile in CFile.__listFilesInUse:
         raise Exception(f"The file '{self.__sFile}' is already in use by another CFile instance.")
      else:
         CFile.__listFilesInUse.append(self.__sFile)

   # eof def __init__(self, sFile=None):

   def __del__(self):
      self.Close()
      if self.__sFile in CFile.__listFilesInUse:
         CFile.__listFilesInUse.remove(self.__sFile)

   # eof def __del__(self):

   def __bIsFreeToUse(self, sFile=None):
      """
Checks if the file ``sFile`` is free to use, that means: not used by another instance of ``CFile``.
      """

      bIsFreeToUse = False # init
      if sFile is None:
         bIsFreeToUse = False # error handling
      else:
         if sFile in CFile.__listFilesInUse:
            bIsFreeToUse = False
         else:
            bIsFreeToUse = True
      return bIsFreeToUse

   # eof def __bIsFreeToUse(self, sFile=None):

   def __OpenForWriting(self):
      """
Opens a text file for writing.

Returns ``bSuccess`` and ``sResult`` (feedback).
      """

      sMethod = "CFile.__OpenForWriting"

      if self.__sFile is None:
         bSuccess = False
         sResult  = "self.__sFile is None; please provide path and name of a file when creating a CFile object."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      try:
         self.__oFileHandle = open(self.__sFile, "w", encoding="utf-8")
         self.__oFileStatus = enFileStatiType.openedforwriting
         bSuccess = True
         sResult  = f"File '{self.__sFile}' is open for writing"
      except Exception as reason:
         self.Close()
         bSuccess = None
         sResult  = f"Not possible to open file '{self.__sFile}' for writing.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def __OpenForWriting(self):

   def __OpenForAppending(self):
      """
Opens a text file for appending.

Returns ``bSuccess`` and ``sResult`` (feedback).
      """

      sMethod = "CFile.__OpenForAppending"

      if self.__sFile is None:
         bSuccess = False
         sResult  = "self.__sFile is None; please provide path and name of a file when creating a CFile object."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      try:
         self.__oFileHandle = open(self.__sFile, "a", encoding="utf-8")
         self.__oFileStatus = enFileStatiType.openedforappending
         bSuccess = True
         sResult  = f"File '{self.__sFile}' is open for appending"
      except Exception as reason:
         self.Close()
         bSuccess = None
         sResult  = f"Not possible to open file '{self.__sFile}' for appending.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def __OpenForAppending(self):

   def __OpenForReading(self):
      """
Opens a text file for reading.

Returns ``bSuccess`` and ``sResult`` (feedback).
      """

      sMethod = "CFile.__OpenForReading"

      if self.__sFile is None:
         bSuccess = False
         sResult  = "self.__sFile is None; please provide path and name of a file when creating a CFile object."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      try:
         self.__oFileHandle = open(self.__sFile, "r", encoding="utf-8")
         self.__oFileStatus = enFileStatiType.openedforreading
         bSuccess = True
         sResult  = f"File '{self.__sFile}' is open for reading"
      except Exception as reason:
         self.Close()
         bSuccess = None
         sResult  = f"Not possible to open file '{self.__sFile}' for reading.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def __OpenForReading(self):

   def Close(self):
      """
Closes the opened file.

**Arguments:**

(no args)

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """
      sMethod = "CFile.Close"

      if self.__oFileHandle is not None:
         try:
            self.__oFileHandle.flush()
            self.__oFileHandle.close()
            bSuccess = True
            sResult  = f"File '{self.__sFile}' closed"
         except Exception as reason:
            bSuccess = None
            sResult  = f"Exception while closing file '{self.__sFile}'.\nReason: " + str(reason)
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         self.__oFileHandle = None
      else:
         bSuccess = True
         sResult  = "Done"

      self.__oFileStatus = enFileStatiType.closed

      return bSuccess, sResult

   # eof def Close(self):

   def Delete(self, bConfirmDelete=True):
      """
Deletes the current file.

**Arguments:**

* ``bConfirmDelete``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  Defines if it will be handled as error if the file does not exist.

  If ``True``: If the file does not exist, the method indicates an error (``bSuccess = False``).

  If ``False``: It doesn't matter if the file exists or not.

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """

      sMethod = "CFile.Delete"

      if self.__sFile is None:
         bSuccess = False
         sResult  = "self.__sFile is None; please provide path and name of a file when creating a CFile object."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if os.path.isfile(self.__sFile) is False:
         if bConfirmDelete is True:
            bSuccess = False
         else:
            bSuccess = True
         sResult = f"Nothing to delete. The file '{self.__sFile}' does not exist."
         return bSuccess, sResult

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      try:
         os.remove(self.__sFile)
         bSuccess = True
         sResult  = f"File '{self.__sFile}' deleted."
      except Exception as reason:
         bSuccess = None
         sResult  = f"Exception while deleting file '{self.__sFile}'.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Delete(self, bConfirmDelete=True):

   def __PrepareOutput(self, Content=""):
      """
Helper for ``Write`` and ``Append`` (consideration of composite data types).

Returns a list of strings (that will be written to file).
      """

      listOut = []

      if type(Content) == list:
         for element in Content:
            listOut.append(str(element))
      elif type(Content) == tuple:
         for element in Content:
            listOut.append(str(element))
      elif type(Content) == set:
         for element in Content:
            listOut.append(str(element))
      elif type(Content) == dict:
         listKeys = Content.keys()
         nRJust = 0
         for key in listKeys:
            sKey = str(key) # because also numerical values can be keys
            if len(sKey) > nRJust:
               nRJust = len(sKey)
         for key in listKeys:
            sKey = str(key) # because also numerical values can be keys
            sOut = sKey.rjust(nRJust, ' ') + " : " + str(Content[key])
            listOut.append(sOut)
      elif str(type(Content)).lower().find('dotdict') >=0:
         try:
            listKeys = Content.keys()
            nRJust = 0
            for key in listKeys:
               sKey = str(key) # because also numerical values can be keys
               if len(sKey) > nRJust:
                  nRJust = len(sKey)
            for key in listKeys:
               sKey = str(key) # because also numerical values can be keys
               sOut = sKey.rjust(nRJust, ' ') + " : " + str(Content[key])
               listOut.append(sOut)
         except Exception as reason:
            listOut.append(str(Content))
      else:
         listOut.append(str(Content))

      return listOut

   # eof def __PrepareOutput(self, Content=""):

   def Write(self, Content="", nVSpaceAfter=0, sPrefix=None, bToScreen=False):
      """
Writes the content of a variable ``Content`` to file.

**Arguments:**

* ``Content``

  / *Condition*: required / *Type*: one of: str, list, tuple, set, dict, dotdict /

  If ``Content`` is not a string, the ``Write`` method resolves the data structure before writing the content to file.

* ``nVSpaceAfter``

  / *Condition*: optional / *Type*: int / *Default*: 0 /

  Adds vertical space ``nVSpaceAfter`` (= number of blank lines) after ``Content``.

* ``sPrefix``

  / *Condition*: optional / *Type*: str / *Default*: None /

  `sPrefix`` is added to every line of output (in case of ``sPrefix`` is not ``None``).

* ``bToScreen``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Prints ``Content`` also to screen (in case of ``bToScreen`` is ``True``).

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """

      sMethod = "CFile.Write"

      if self.__oFileStatus != enFileStatiType.openedforwriting:
         bSuccess, sResult = self.__OpenForWriting()
         if bSuccess is not True:
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

      listOut = self.__PrepareOutput(Content)

      for nCnt in range(nVSpaceAfter):
         listOut.append("")

      if bToScreen is True:
         for sOut in listOut:
            if ( (sPrefix is not None) and (sOut != '') ):
               sOut = f"{sPrefix}{sOut}"
            print(sOut)

      bSuccess = True
      sResult  = "Done"
      try:
         for sOut in listOut:
            if ( (sPrefix is not None) and (sOut != '') ):
               sOut = f"{sPrefix}{sOut}"
            self.__oFileHandle.write(sOut + "\n")
      except Exception as reason:
         bSuccess = None
         sResult  = f"Not possible to write to file '{self.__sFile}'.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Write(self, Content="", nVSpaceAfter=0, sPrefix=None, bToScreen=False):

   def Append(self, Content="", nVSpaceAfter=0, sPrefix=None, bToScreen=False):
      """
Appends the content of a variable ``Content`` to file.

**Arguments:**

* ``Content``

  / *Condition*: required / *Type*: one of: str, list, tuple, set, dict, dotdict /

  If ``Content`` is not a string, the ``Write`` method resolves the data structure before writing the content to file.

* ``nVSpaceAfter``

  / *Condition*: optional / *Type*: int / *Default*: 0 /

  Adds vertical space ``nVSpaceAfter`` (= number of blank lines) after ``Content``.

* ``sPrefix``

  / *Condition*: optional / *Type*: str / *Default*: None /

  `sPrefix`` is added to every line of output (in case of ``sPrefix`` is not ``None``).

* ``bToScreen``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  Prints ``Content`` also to screen (in case of ``bToScreen`` is ``True``).

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """
      sMethod = "CFile.Append"

      if self.__oFileStatus != enFileStatiType.openedforappending:
         bSuccess, sResult = self.__OpenForAppending()
         if bSuccess is not True:
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

      listOut = self.__PrepareOutput(Content)

      for nCnt in range(nVSpaceAfter):
         listOut.append("")

      if bToScreen is True:
         for sOut in listOut:
            if ( (sPrefix is not None) and (sOut != '') ):
               sOut = f"{sPrefix}{sOut}"
            print(sOut)

      bSuccess = True
      sResult  = "Done"
      try:
         for sOut in listOut:
            if ( (sPrefix is not None) and (sOut != '') ):
               sOut = f"{sPrefix}{sOut}"
            self.__oFileHandle.write(sOut + "\n")
      except Exception as reason:
         bSuccess = None
         sResult  = f"Not possible to append to file '{self.__sFile}'.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Append(self, Content="", nVSpaceAfter=0, sPrefix=None, bToScreen=False):

   def ReadLines(self,
                 bCaseSensitive  = True,
                 bSkipBlankLines = False,
                 sComment        = None,
                 sStartsWith     = None,
                 sEndsWith       = None,
                 sStartsNotWith  = None,
                 sEndsNotWith    = None,
                 sContains       = None,
                 sContainsNot    = None,
                 sInclRegEx      = None,
                 sExclRegEx      = None,
                 bLStrip         = False,
                 bRStrip         = True,
                 bToScreen       = False):
      """
Reads content from current file. Returns an array of lines together with ``bSuccess`` and ``sResult`` (feedback).

The method takes care of opening and closing the file. The complete file content is read by ``ReadLines`` in one step,
but with the help of further parameters it is possible to reduce the content by including and excluding lines.

Internally ``ReadLines`` uses the string filter method ``StringFilter``. All filter related input parameter of
``ReadLines`` and ``StringFilter`` are the same.

The logical join of all filter is: ``AND``.

**Arguments:**

* ``bCaseSensitive``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  * If ``True``, the standard filters work case sensitive, otherwise not.
  * This has no effect to the regular expression based filters ``sInclRegEx`` and ``sExclRegEx``.

* ``bSkipBlankLines``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True``, blank lines will be skipped, otherwise not.

* ``sComment``

  / *Condition*: optional / *Type*: str / *Default*: None /

  In case of a line starts with the string ``sComment``, this line is skipped.

* ``sStartsWith``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string starts with the string ``sStartsWith``
  * More than one string can be provided (semicolon separated; logical join: ``OR``)

* ``sEndsWith``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string ends with the string ``sEndsWith``
  * More than one string can be provided (semicolon separated; logical join: ``OR``)

* ``sStartsNotWith``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string starts not with the string ``sStartsNotWith``
  * More than one string can be provided (semicolon separated; logical join: ``AND``)

* ``sEndsNotWith``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string ends not with the string ``sEndsNotWith``
  * More than one string can be provided (semicolon separated; logical join: ``AND``)

* ``sContains``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string contains the string ``sContains`` at any position
  * More than one string can be provided (semicolon separated; logical join: ``OR``)

* ``sContainsNot``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * The criterion of this filter is fulfilled in case of the input string does **not** contain the string ``sContainsNot`` at any position
  * More than one string can be provided (semicolon separated; logical join: ``AND``)

* ``sInclRegEx``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * *Include* filter based on regular expressions (consider the syntax of regular expressions!)
  * The criterion of this filter is fulfilled in case of the regular expression ``sInclRegEx`` matches the input string
  * Leading and trailing blanks within the input string are considered
  * ``bCaseSensitive`` has no effect
  * A semicolon separated list of several regular expressions is **not** supported

* ``sExclRegEx``

  / *Condition*: optional / *Type*: str / *Default*: None /

  * *Exclude* filter based on regular expressions (consider the syntax of regular expressions!)
  * The criterion of this filter is fulfilled in case of the regular expression ``sExclRegEx`` does **not** match the input string
  * Leading and trailing blanks within the input string are considered
  * ``bCaseSensitive`` has no effect
  * A semicolon separated list of several regular expressions is **not** supported

* ``bLStrip``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True``, leading spaces are removed from line before the filters are used, otherwise not.

* ``bRStrip``

  / *Condition*: optional / *Type*: bool / *Default*: True /

  If ``True``, trailing spaces are removed from line before the filters are used, otherwise not.

* ``bToScreen``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  If ``True``, the content read from file is also printed to screen, otherwise not.
      """

      sMethod = "CFile.ReadLines"

      listLines = []

      if os.path.isfile(self.__sFile) is False:
         bSuccess = False
         sResult  = f"The file '{self.__sFile}' does not exist."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return listLines, bSuccess, sResult

      # !!! independend from:  self.__oFileStatus != enFileStatiType.openedforreading: !!!
      # Reason: Repeated call of ReadLines needs to have the read pointer at the beginning of the file.
      bSuccess, sResult = self.__OpenForReading()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return listLines, bSuccess, sResult

      try:
         sFileContent = self.__oFileHandle.read()
      except Exception as reason:
         bSuccess = None
         sResult  = f"Not possible to read from file '{self.__sFile}'.\nReason: " + str(reason)
         return listLines, bSuccess, sResult

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return listLines, bSuccess, sResult

      listFileContent = sFileContent.splitlines() # in opposite to readlines this is OS independend!

      for sLine in listFileContent:
         if CString.StringFilter(sString           = sLine,
                                 bCaseSensitive    = bCaseSensitive,
                                 bSkipBlankStrings = bSkipBlankLines,
                                 sComment          = sComment,
                                 sStartsWith       = sStartsWith,
                                 sEndsWith         = sEndsWith,
                                 sStartsNotWith    = sStartsNotWith,
                                 sEndsNotWith      = sEndsNotWith,
                                 sContains         = sContains,
                                 sContainsNot      = sContainsNot,
                                 sInclRegEx        = sInclRegEx,
                                 sExclRegEx        = sExclRegEx,
                                 bDebug            = False) is True:
            if bLStrip is True:
               sLine = sLine.lstrip(" \t\r\n")

            if bRStrip is True:
               sLine = sLine.rstrip(" \t\r\n")

            if bToScreen is True:
               print(sLine)

            listLines.append(sLine)

      # eof for sLine in listFileContent:

      del listFileContent

      nNrOfLines = len(listLines)

      bSuccess = True
      sResult  = f"Read {nNrOfLines} lines from '{self.__sFile}'."
      return listLines, bSuccess, sResult

   # eof def ReadLines(...)

   def GetFileInfo(self):
      """
Returns the following informations about the file (encapsulated within a dictionary ``dFileInfo``):

**Returns:**

* Key ``sFile``

  / *Type*: str /

  Path and name of current file


* Key ``bFileIsExisting``

  / *Type*: bool /

  ``True`` if file is existing, otherwise ``False``

* Key ``sFileName``

  / *Type*: str /

  The name of the current file (incl. extension)

* Key ``sFileExtension``

  / *Type*: str /

  The extension of the current file

* Key ``sFileNameOnly``

  / *Type*: str /

  The pure name of the current file (without extension)

* Key ``sFilePath``

  / *Type*: str /

  The the path to current file

* Key ``bFilePathIsExisting``

  / *Type*: bool /

  ``True`` if file path is existing, otherwise ``False``
      """

      sMethod = "CFile.GetFileInfo"

      dFileInfo = {}
      dFileInfo['sFile']               = None
      dFileInfo['bFileIsExisting']     = None
      dFileInfo['sFileName']           = None
      dFileInfo['sFileExtension']      = None
      dFileInfo['sFileNameOnly']       = None
      dFileInfo['sFilePath']           = None
      dFileInfo['bFilePathIsExisting'] = None

      if self.__sFile is None:
         return None

      dFileInfo['sFile']           = self.__sFile
      dFileInfo['bFileIsExisting'] = os.path.isfile(self.__sFile)

      sFileName = os.path.basename(self.__sFile)
      dFileInfo['sFileName'] = sFileName

      sFileExtension = ""
      sFileNameOnly  = ""
      listParts = sFileName.split('.')
      if len(listParts) > 1:
         sFileExtension = listParts[len(listParts)-1]
         sFileNameOnly  = sFileName[:-len(sFileExtension)-1]
      else:
         sFileExtension = ""
         sFileNameOnly  = sFileName

      dFileInfo['sFileExtension']      = sFileExtension
      dFileInfo['sFileNameOnly']       = sFileNameOnly
      dFileInfo['sFilePath']           = os.path.dirname(self.__sFile)
      dFileInfo['bFilePathIsExisting'] = os.path.isdir(dFileInfo['sFilePath'])

      return dFileInfo

   # eof def GetFileInfo(self):

   def CopyTo(self, sDestination=None, bOverwrite=False):
      """
Copies the current file to ``sDestination``, that can either be a path without file name or a path together with a file name.

In case of the destination file already exists and ``bOverwrite`` is ``True``, than the destination file will be overwritten.

In case of the destination file already exists and ``bOverwrite`` is ``False`` (default), than the destination file will not be overwritten
and ``CopyTo`` returns ``bSuccess = False``.

**Arguments:**

* ``sDestination``

  / *Condition*: required / *Type*: string /

  The path to destination file (either incl. file name or without file name)

* ``bOverwrite``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  * In case of the destination file already exists and ``bOverwrite`` is ``True``, than the destination file will be overwritten.
  * In case of the destination file already exists and ``bOverwrite`` is ``False`` (default), than the destination file will not be overwritten
    and ``CopyTo`` returns ``bSuccess = False``.

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """
      sMethod = "CFile.CopyTo"

      if self.__sFile is None:
         bSuccess = False
         sResult  = "self.__sFile is None; please provide path and name of a file when creating a CFile object."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if os.path.isfile(self.__sFile) is False:
         bSuccess = False
         sResult  = f"The file '{self.__sFile}' does not exist, therefore nothing can be copied."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if sDestination is None:
         bSuccess = False
         sResult  = "sDestination is None; please provide path and name of destination file. Or at least the destination path. In this case the file name will be taken over."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      sDestination = CString.NormalizePath(sDestination)

      bDeleteDestFile = False

      sDestFile = sDestination # default

      if os.path.isdir(sDestination) is True:
         sFileName = os.path.basename(self.__sFile)
         sDestFile = f"{sDestination}/{sFileName}" # file name in destination is required for: shutil.copyfile

      if self.__bIsFreeToUse(sDestFile) is False:
         bSuccess = False
         sResult  = f"The destination file '{sDestFile}' is already in use by another CFile instance."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      self.__sLastDestination = sDestFile

      if os.path.isfile(sDestFile) is True:
         # destination file already exists
         if sDestFile == self.__sFile:
            bSuccess = False
            sResult  = f"Source file and destination file are the same: '{self.__sFile}'. Therefore nothing to do."
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

         if bOverwrite is True:
            bDeleteDestFile = True
         else:
            bSuccess = False
            sResult  = f"Not allowed to overwrite existing destination file '{sDestFile}'. Therefore nothing to do."
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult
      else:
         # destination file not yet exists
         # (we assume here that the destination shall be a file because we already have figured out that the destination is not a folder)
         # => we have to check if the path to the file exists
         sDestFilePath = os.path.dirname(sDestFile)
         if os.path.isdir(sDestFilePath) is True:
            bDeleteDestFile = False
         else:
            bSuccess = False
            sResult  = f"The destination path '{sDestFilePath}' does not exist. The file '{self.__sFile}' cannot be copied."
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

      # eof else - if os.path.isfile(sDestFile) is True:

      # analysis done, now the action

      bSuccess, sResult = self.Close()
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if bDeleteDestFile is True:
         # To delete the destination file explicitely before executing any copy-function is an addon here in this library.
         # The purpose is to be independend from the way the used copy function is handling existing destination files.
         # But this makes only sense under Windows and not under Linux, because Windows is much more strict with access
         # violations than Linux. Therefore we avoid such kind of additional steps in case of the platform is not Windows.
         if platform.system() == "Windows":
            try:
               os.remove(sDestFile)
               bSuccess = True
               sResult  = f"File '{sDestFile}' deleted."
            except Exception as reason:
               bSuccess = None
               sResult  = f"Exception while deleting destination file '{sDestFile}'.\nReason: " + str(reason)
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
               return bSuccess, sResult
      # eof if bDeleteDestFile is True:

      try:
         shutil.copyfile(self.__sFile, sDestFile)
         bSuccess = True
         sResult  = f"File '{self.__sFile}' copied to '{sDestFile}'."
      except Exception as reason:
         bSuccess = None
         sResult  = f"Exception while copying file '{self.__sFile}' to '{sDestFile}'.\nReason: " + str(reason)
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def CopyTo(self, sDestination=None, bOverwrite=False):

   def MoveTo(self, sDestination=None, bOverwrite=False):
      """
Moves the current file to ``sDestination``, that can either be a path without file name or a path together with a file name.

**Arguments:**

* ``sDestination``

  / *Condition*: required / *Type*: string /

  The path to destination file (either incl. file name or without file name)

* ``bOverwrite``

  / *Condition*: optional / *Type*: bool / *Default*: False /

  * In case of the destination file already exists and ``bOverwrite`` is ``True``, than the destination file will be overwritten.
  * In case of the destination file already exists and ``bOverwrite`` is ``False`` (default), than the destination file will not be overwritten
    and ``MoveTo`` returns ``bSuccess = False``.

**Returns:**

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation was successful or not

* ``sResult``

  / *Type*: str /

  Contains details about what happens during computation
      """
      sMethod = "CFile.MoveTo"

      bSuccess, sResult = self.CopyTo(sDestination, bOverwrite)
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if os.path.isfile(self.__sLastDestination) is False:
         # the copied file should exist at new location
         bSuccess = None
         sResult  = f"Someting went wrong while copying the file '{self.__sFile}' to '{self.__sLastDestination}'. Aborting."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult
      else:
         bSuccess, sResult = self.Delete()
         if bSuccess is not True:
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

      bSuccess = True
      sResult  = f"File moved from '{self.__sFile}' to '{self.__sLastDestination}'"
      return bSuccess, sResult

   # eof def MoveTo(self, sDestination=None, bOverwrite=False):

# eof class CFile(object):
