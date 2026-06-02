Set WshShell = CreateObject("WScript.Shell")

' Run launcher.pyw hidden, wait for it to finish
WshShell.Run "pythonw launcher.pyw", 0, True
