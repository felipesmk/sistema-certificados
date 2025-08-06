@echo off
echo ========================================
echo    CONFIGURACAO AUTOMATICA DA VM
echo ========================================
echo.

echo [1/8] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Baixe e instale Python 3.8+ de: https://python.org
    pause
    exit /b 1
)

echo [2/8] Verificando Git...
git --version
if %errorlevel% neq 0 (
    echo ERRO: Git nao encontrado!
    echo Baixe e instale Git de: https://git-scm.com
    pause
    exit /b 1
)

echo [3/8] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo [4/8] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo [5/8] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo [6/8] Configurando banco de dados...
python quick_setup.py setup
if %errorlevel% neq 0 (
    echo ERRO: Falha na configuracao do banco!
    pause
    exit /b 1
)

echo [7/8] Verificando status do sistema...
python manage_db.py status
if %errorlevel% neq 0 (
    echo ERRO: Falha na verificacao do status!
    pause
    exit /b 1
)

echo [8/8] Iniciando aplicacao...
echo.
echo ========================================
echo    CONFIGURACAO CONCLUIDA!
echo ========================================
echo.
echo Acesse: http://localhost:5000
echo Usuario admin: admin
echo Senha: (a que voce definiu)
echo.
echo Para parar: Ctrl+C
echo Para reiniciar: python app.py
echo.
python app.py 