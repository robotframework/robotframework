# **************************************************************************************************************
#
#  Copyright 2020-2024 Robert Bosch GmbH
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
#
# **************************************************************************************************************
#
# CComparison.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 03.04.2023
#
# **************************************************************************************************************

# -- import standard Python modules
import os, re

# -- import own Python modules
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.String.CString import CString

# **************************************************************************************************************

class CComparison(object):
   """The class ``CComparison`` contains mechanisms to compare two files either based on the original version of these files
or based on an extract (made with regular expressions) to ensure that only relevant parts of the files are compared.
   """

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __init__(self):
      self.__bSkipBlankLines = True

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Compare(self, sFile_1=None, sFile_2=None, sPatternFile=None, sIgnorePatternFile=None, bDebug=False):
      """
Compares two files. While reading in all files empty lines are skipped.

**Arguments:**

* ``sFile_1``

  / *Condition*: required / *Type*: str /

  First file used for comparison.

* ``sFile_2``

  / *Condition*: required / *Type*: str /

  Second file used for comparison.

* ``sPatternFile``

  / *Condition*: optional / *Type*: str  / *Default*: None /

  Pattern file containing a set of regular expressions (line by line). The regular expressions are used to make
  an extract of both input files. In this case the extracts are compared (instead of the original file content).

* ``sIgnorePatternFile``

  / *Condition*: optional / *Type*: str  / *Default*: None /

  Pattern file containing a set of strings (**not** regular expressuions; line by line). Every line containing one
  of the strings, is skipped.

**Returns:**

* ``bIdentical``

  / *Type*: bool /

  Indicates if the two input files (or their extracts) have the same content or not.

* ``bSuccess``

  / *Type*: bool /

  Indicates if the computation of the method was successful or not.

* ``sResult``

  / *Type*: str /

  The result of the computation of the method.
      """

      sMethod = "CComparison.Compare"

      bIdentical = None
      bSuccess   = None
      sResult    = "unknown"

      if sFile_1 is None:
         bSuccess = False
         sResult  = "sFile_1 is None"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if sFile_2 is None:
         bSuccess = False
         sResult  = "sFile_2 is None"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      sFile_1 = CString.NormalizePath(sFile_1)
      sFile_2 = CString.NormalizePath(sFile_2)

      if sFile_1 == sFile_2:
         bSuccess = False
         sResult  = f"Path and name of input files are the same."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if os.path.isfile(sFile_1) is False:
         bSuccess = False
         sResult  = f"The file '{sFile_1}' does not exist"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if os.path.isfile(sFile_2) is False:
         bSuccess = False
         sResult  = f"The file '{sFile_2}' does not exist"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if sPatternFile is not None:
         # (optional)
         sPatternFile = CString.NormalizePath(sPatternFile)
         if os.path.isfile(sPatternFile) is False:
            bSuccess = False
            sResult  = f"The file '{sPatternFile}' does not exist"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bIdentical, bSuccess, sResult
      # eof if sPatternFile is not None:

      sIgnorePatterns    = None
      listIgnorePatterns = None

      if sIgnorePatternFile is not None:
         # (optional)
         sIgnorePatternFile = CString.NormalizePath(sIgnorePatternFile)
         if os.path.isfile(sIgnorePatternFile) is False:
            bSuccess = False
            sResult  = f"The file '{sIgnorePatternFile}' does not exist"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bIdentical, bSuccess, sResult
         oIgnorePatternFile = CFile(sIgnorePatternFile)
         listIgnorePatterns, bSuccess, sResult = oIgnorePatternFile.ReadLines()
         del oIgnorePatternFile
         if bSuccess is not True:
            return bIdentical, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
         if listIgnorePatterns is not None:
            sIgnorePatterns = ";".join(listIgnorePatterns)
      # eof if sIgnorePatternFile is not None:

      if bDebug is True:
         print()
         print("[FILE 1]")
      oFile_1 = CFile(sFile_1)
      listLines_1, bSuccess, sResult = oFile_1.ReadLines(bSkipBlankLines=self.__bSkipBlankLines, sContainsNot=sIgnorePatterns, bLStrip=True, bRStrip=True, bToScreen=bDebug)
      del oFile_1
      if bSuccess is False:
         del listLines_1
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if bDebug is True:
         print()
         print("[FILE 2]")
      oFile_2 = CFile(sFile_2)
      listLines_2, bSuccess, sResult = oFile_2.ReadLines(bSkipBlankLines=self.__bSkipBlankLines, sContainsNot=sIgnorePatterns, bLStrip=True, bRStrip=True, bToScreen=bDebug)
      del oFile_2
      if bSuccess is False:
         del listLines_1
         del listLines_2
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         return bIdentical, bSuccess, sResult

      if sPatternFile is None:
         # no pattern given => compare the original version of the files

         # -- check number of lines
         nNrOfLines_1 = len(listLines_1)
         nNrOfLines_2 = len(listLines_2)
         if nNrOfLines_1 != nNrOfLines_2:
            del listLines_1
            del listLines_2
            bIdentical = False
            bSuccess   = True
            sResult    = f"The files contain different number of lines (file 1: {nNrOfLines_1} lines, file 2: {nNrOfLines_2} lines"
            return bIdentical, bSuccess, sResult

         for nIndex, sLine_1 in enumerate(listLines_1):
            sLine_2 = listLines_2[nIndex]
            if sLine_1 != sLine_2:
               del listLines_1
               del listLines_2
               bIdentical = False
               bSuccess   = True
               sResult    = f"Found deviating lines\n(1) '{sLine_1}'\n(2) '{sLine_2}'"
               return bIdentical, bSuccess, sResult
      else:
         if bDebug is True:
            print()
            print("[PATTERN]")
         # -- read pattern for comparison of files
         oPatternFile = CFile(sPatternFile)
         listPatterns, bSuccess, sResult = oPatternFile.ReadLines(bSkipBlankLines=True, bLStrip=True, bRStrip=True, bToScreen=bDebug)
         del oPatternFile
         if bSuccess is False:
            del listPatterns
            sResult = CString.FormatResult(sMethod, bSuccess, sResult)
            return bIdentical, bSuccess, sResult
         # -- compile pattern for comparison of files
         listRegEx = []
         for sPattern in listPatterns:
            listRegEx.append(re.compile(sPattern))
         del listPatterns
         # -- apply pattern to content of file 1
         listSubsetLines_1 = []
         for sLine in listLines_1:
            listLineParts_1 = []
            for RegEx in listRegEx:
               listPositions = RegEx.findall(sLine)
               if len(listPositions) > 0:
                  for position in listPositions:
                     if isinstance(position, (tuple, list)):
                        for subposition in position:
                           listLineParts_1.append(subposition)
                     else:
                        listLineParts_1.append(position)
                  sLineNew_1 = " || ".join(listLineParts_1)
                  listSubsetLines_1.append(sLineNew_1)
                  break # for RegEx in listRegEx:
         # eof for sLine in listLines_1:
         del listLines_1
         # -- apply pattern to content of file 2
         listSubsetLines_2 = []
         for sLine in listLines_2:
            listLineParts_2 = []
            for RegEx in listRegEx:
               listPositions = RegEx.findall(sLine)
               if len(listPositions) > 0:
                  for position in listPositions:
                     if isinstance(position, (tuple, list)):
                        for subposition in position:
                           listLineParts_2.append(subposition)
                     else:
                        listLineParts_2.append(position)
                  sLineNew_2 = " || ".join(listLineParts_2)
                  listSubsetLines_2.append(sLineNew_2)
                  break # for RegEx in listRegEx:
         # eof for sLine in listLines_2:
         del listLines_2
         del listRegEx

         # -- check number of lines
         nNrOfSubsetLines_1 = len(listSubsetLines_1)
         nNrOfSubsetLines_2 = len(listSubsetLines_2)
         if nNrOfSubsetLines_1 != nNrOfSubsetLines_2:
            print()
            print(120*"-")
            print("[SUBSET 1]")
            sSubset1 = "\n".join(listSubsetLines_1)
            print(f"{sSubset1}")
            print(120*"-")
            print("[SUBSET 2]")
            sSubset2 = "\n".join(listSubsetLines_2)
            print(f"{sSubset2}")
            print(120*"-")
            print()
            del listSubsetLines_1
            del listSubsetLines_2
            bIdentical = False
            bSuccess   = True
            sResult    = f"The subsets of files contain different number of lines (subset 1: {nNrOfSubsetLines_1} lines, subset 2: {nNrOfSubsetLines_2} lines"
            return bIdentical, bSuccess, sResult

         # -- compare subsets of content
         for nIndex, sLine_1 in enumerate(listSubsetLines_1):
            sLine_2 = listSubsetLines_2[nIndex]
            if sLine_1 != sLine_2:
               del listSubsetLines_1
               del listSubsetLines_2
               if bDebug is True:
                  print()
                  print(120*"-")
                  print("[SUBSET 1]")
                  sSubset1 = "\n".join(listSubsetLines_1)
                  print(f"{sSubset1}")
                  print(120*"-")
                  print("[SUBSET 2]")
                  sSubset2 = "\n".join(listSubsetLines_2)
                  print(f"{sSubset2}")
                  print(120*"-")
                  print()
               bIdentical = False
               bSuccess   = True
               sResult    = f"Found deviating lines\n(1) '{sLine_1}'\n(2) '{sLine_2}'"
               return bIdentical, bSuccess, sResult
         # eof for nIndex, sLine_1 in enumerate(listSubsetLines_1):
         del listSubsetLines_1
         del listSubsetLines_2

      # eof else - if sPatternFile is None:

      # final result
      bIdentical = True
      bSuccess   = True
      sResult    = "Both files have same content"

      return bIdentical, bSuccess, sResult

   # eof def Compare(self, sFile_1=None, sFile_2=None, sPatternFile=None):

# eof class CComparison(object):

# --------------------------------------------------------------------------------------------------------------







