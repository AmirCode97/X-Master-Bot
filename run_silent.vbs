Set WshShell = CreateObject("WScript.Shell") 
WshShell.CurrentDirectory = "C:\Users\amirs\.gemini\antigravity\scratch\x-bot\" 
WshShell.Run "python main.py", 0, True 
