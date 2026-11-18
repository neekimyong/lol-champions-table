@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo .venv bulunamadi. Once bunlari calistir:
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install PySide6 PyInstaller
  pause
  exit /b 1
)
echo Derleniyor...
if exist "dist\data" rmdir /s /q "dist\data"
if exist "dist\assets" rmdir /s /q "dist\assets"
.venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --name "LoLKahramanlari" ^
  --add-data "%~dp0data;data" --add-data "%~dp0assets;assets" ^
  --distpath dist --workpath build --specpath build src\main.py
echo.
echo Bitti: dist\LoLKahramanlari.exe
pause
