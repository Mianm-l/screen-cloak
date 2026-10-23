Set WshShell = CreateObject("WScript.Shell")
strCurrentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strCurrentDir
WshShell.Run "pythonw main.py", 0, False
Set WshShell = Nothing
