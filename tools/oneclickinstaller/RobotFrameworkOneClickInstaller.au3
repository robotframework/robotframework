;;  Copyright 2008-2009 Nokia Siemens Networks Oyj
;;
;;  Licensed under the Apache License, Version 2.0 (the "License");
;;  you may not use this file except in compliance with the License.
;;  You may obtain a copy of the License at
;;
;;      http://www.apache.org/licenses/LICENSE-2.0
;;
;;  Unless required by applicable law or agreed to in writing, software
;;  distributed under the License is distributed on an "AS IS" BASIS,
;;  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
;;  See the License for the specific language governing permissions and
;;  limitations under the License.


;; Robot Framework One Click Installer for Windows
;;
;; This installer installs Robot Framework and its preconditions Python and 
;; Jython (optional). If installer is executed without arguments, it opens a 
;; dialog explaining the options and asking the user to enter the installation
;; directory. If a command line options is given, it must be a path to an 
;; existing directory and it is used as installation directory.
;;
;; For more information about this script see $USAGE below. To learn more 
;; about silent Python installation, see url [1]. Silent Jython installation 
;; options can be seen with command [2].
;;
;; [1] http://www.python.org/download/releases/2.5/msi/#automated
;; [2] java -jar jython_installer-2.2.x.jar --help


;;
;; Config
;;

; Expected patterns for installer names and target directory names.
$PYTHON_DIR_NAME = "Python"
$JYTHON_DIR_NAME = "Jython"
$PYTHON_PATTERN = "python-2.*.msi"
$ROBOT_PATTERN = "robotframework-2.*.exe"
$JYTHON_PATTERN = "jython_installer-2.*.jar"

$USAGE = "One Click Installer installs Robot Framework and its " & _
         "preconditions Python and Jython (optional)." & @CRLF & @CRLF & _
         "Please specify the directory where you want software to be " & _
         "installed. Also make sure that you have required Robot Framework " & _
         "and Python installers, and optionally Jython installer, in the " & _
         "same directory as this installer." & @CRLF & @CRLF & _
         "For more information see http://robotframework.org/."

;;
;; Main
;;

$base_dir = GetBaseDirectory()
$python_installer = GetRequiredInstaller($PYTHON_PATTERN, "Python")
$robot_installer = GetRequiredInstaller($ROBOT_PATTERN, "Robot Framework")
$jython_installer = GetOptionalInstaller($JYTHON_PATTERN)
$python_dir = GetPythonDir($base_dir & $PYTHON_DIR_NAME)
$jython_dir = GetJythonDir($base_dir & $JYTHON_DIR_NAME, $jython_installer)
InstallPython($python_installer, $python_dir)
InstallJython($jython_installer, $jython_dir)
SetPath($python_dir, $jython_dir)  ; This must be done before InstallRobot to always have msvcrt71.dll in PATH
InstallRobot($robot_installer)
Exit


;;
;; Functions
;;

Func GetBaseDirectory()
    If $CmdLine[0] == 0 Then
        $base = InputBox("Robot Framework One Click Installer", $USAGE, "C:\", "", 400, 250)
    ElseIf $CmdLine[0] == 1 Then
        $base = $CmdLine[1]
    Else
        Cancel("Usage: " & @ScriptName & " [basedir]")
    EndIf
    If $base == "" Then
        Cancel("Installation cancelled by user.")
    ElseIf FileExists($base) == 0 Then
        Cancel("Given directory doesn't exist.")
    ElseIf StringRight($base, 1) <> "\" Then
        $base = $base & "\"
    EndIf
    Return $base
EndFunc


Func Cancel($msg)
    MsgBox(0, "Installation Cancelled", $msg)
    Exit
EndFunc


Func GetRequiredInstaller($pattern, $name)
    $installer = GetOptionalInstaller($pattern)
    If $installer == "" Then
        Cancel("Could not find " & $name & " installer with pattern '" & $pattern & "'")
    Endif
    return $installer
EndFunc


Func GetOptionalInstaller($pattern)
    $found = FileFindFirstFile($pattern)
    If $found == -1 Then
        $installer = ""
    Else 
        $installer = FileFindNextFile($found)
    EndIf
    FileClose($found)
    return $installer
EndFunc


Func GetPythonDir($dir)
    VerifyInstallationDir($dir, "Python")
    return $dir
EndFunc


Func GetJythonDir($dir, $installer)
    If $installer == "" Then
        return ""
    EndIf
    VerifyInstallationDir($dir, "Jython")
    return $dir
EndFunc


Func VerifyInstallationDir($dir, $name)
    If FileExists($dir) == 1 Then
        Cancel($name & " installation directory '" & $dir & "' already exists.")
    EndIf
EndFunc


Func InstallPython($installer, $dir)
    $cmd = "msiexec /i " & $installer & " TARGETDIR=""" & $dir & """ /qb!" 
    RunWait($cmd)   
EndFunc


Func InstallJython($installer, $dir)
    If $installer == "" Then
        return
    EndIf
    $cmd = "java -jar " & $installer & " -s -d """ & $dir & """"
    RunWait($cmd)
EndFunc


Func InstallRobot($installer)
    Run($installer)
    WaitSetupWindowAndClickEnter("This Wizard will install")
    WaitSetupWindowAndClickEnter("Select python installation")
    WaitSetupWindowAndClickEnter("Ready to install")
    WaitSetupWindowAndClickEnter("Postinstall script finished")
EndFunc


Func WaitSetupWindowAndClickEnter($exp_text)
    WinWaitActive("Setup", $exp_text) 
    Send("{ENTER}")
EndFunc


Func SetPath($python, $jython)
    $update = $python & ";" & $python & "\Scripts;" & $jython
    $orig = RegRead("HKCU\Environment", "PATH")

    If $orig == "" Then
        $new = $update
    ElseIf StringRight($orig, 1) == ";" Then
        $new = $orig & $update
    Else
        $new = $orig & ";" & $update
    EndIf
    
    RegWrite("HKCU\Environment", "PATH", "REG_EXPAND_SZ", $new)
    EnvUpdate()
EndFunc
