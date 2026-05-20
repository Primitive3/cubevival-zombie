@echo off
REM Build script for Windows - creates standalone executable
REM Requires Python and PyInstaller installed

echo Installing dependencies...
pip install pygame pyinstaller

echo Building executable...
pyinstaller --onefile --windowed --name "SobrevivienteSinCV" ^
  --distpath "." ^
  main.py

echo Done! Executable created: SobrevivienteSinCV.exe
pause
