@echo off
echo ========================================
echo    CONFIGURACAO AUTOMATICA DA VM
echo ========================================
echo.

echo [1/10] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Baixe e instale Python 3.8+ de: https://python.org
    pause
    exit /b 1
)

echo [2/10] Verificando Git...
git --version
if %errorlevel% neq 0 (
    echo ERRO: Git nao encontrado!
    echo Baixe e instale Git de: https://git-scm.com
    pause
    exit /b 1
)

echo [3/10] Criando ambiente virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar ambiente virtual!
    pause
    exit /b 1
)

echo [4/10] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo [5/10] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo [6/10] Configurando PostgreSQL...
python configure_postgresql.py
if %errorlevel% neq 0 (
    echo ERRO: Falha na configuracao do PostgreSQL!
    pause
    exit /b 1
)

echo [7/10] Configurando banco de dados...
python quick_setup.py setup
if %errorlevel% neq 0 (
    echo ERRO: Falha na configuracao do banco!
    pause
    exit /b 1
)

echo [8/10] Verificando status do sistema...
python manage_db.py status
if %errorlevel% neq 0 (
    echo ERRO: Falha na verificacao do status!
    pause
    exit /b 1
)

echo [9/10] Configurando firewall...
netsh advfirewall firewall add rule name="Sistema Certificados Dev" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Sistema Certificados Prod" dir=in action=allow protocol=TCP localport=80

echo [10/10] Iniciando aplicacao...
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