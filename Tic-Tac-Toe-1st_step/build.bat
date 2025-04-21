@echo off
setlocal

:: Create build directory
mkdir dist

:: Build the executable
pyinstaller --onefile --noconsole ^
  --icon="Tic Tac Toe 2.0.ico" ^
  --version-file="version.txt" ^
  "Tic Tac Toe 2.0.py"

:: Copy music file
copy "background.mp3" dist\

:: Move final files
mkdir Final
move dist\*.exe Final\
move dist\background.mp3 Final\

echo Done!
pause
