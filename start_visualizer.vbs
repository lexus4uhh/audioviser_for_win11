Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\Alexey\OneDrive\Documents\IT\audiovizer"
WshShell.Run "cmd /c capture_system_audio.exe | python visualize_audio.py", 0, False