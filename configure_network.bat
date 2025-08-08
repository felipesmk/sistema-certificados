@echo off
echo ========================================
echo    CONFIGURACAO DE REDE E FIREWALL
echo ========================================
echo.

echo [1/4] Obtendo IP da VM...
ipconfig | findstr "IPv4"
echo.

echo [2/4] Verificando porta 80...
netstat -ano | findstr :80
if %errorlevel% equ 0 (
    echo AVISO: Porta 80 ja esta em uso!
    echo.
)

echo [3/4] Configurando firewall...
REM Criar regra para a porta 80 (HTTP)
netsh advfirewall firewall add rule name="Sistema Certificados HTTP" dir=in action=allow protocol=TCP localport=80
if %errorlevel% equ 0 (
    echo Firewall configurado com sucesso!
) else (
    echo ERRO: Falha ao configurar firewall!
    echo Execute como administrador.
)

echo [4/4] Testando conectividade...
echo Testando localhost...
curl -s http://localhost >nul 2>&1
if %errorlevel% equ 0 (
    echo Localhost: OK
) else (
    echo Localhost: FALHOU (aplicacao nao esta rodando)
)

echo.
echo ========================================
echo    CONFIGURACAO DE REDE CONCLUIDA
echo ========================================
echo.
echo Para acessar de outras maquinas:
echo http://[IP-DA-VM]
echo.
echo Para verificar IP novamente: ipconfig
echo Para testar conectividade: curl http://localhost
echo.
pause 