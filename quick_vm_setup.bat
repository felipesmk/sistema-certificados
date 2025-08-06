@echo off
echo Configurando VM rapidamente...
call venv\Scripts\activate.bat
pip install -r requirements.txt
python quick_setup.py setup
echo.
echo Pronto! Execute: python app.py 