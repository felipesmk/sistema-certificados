#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO AUTOMATICA SUSE VM"
echo "========================================"
echo

# Detectar versão do SUSE
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Sistema detectado: $PRETTY_NAME"
    echo "Versão: $VERSION"
    echo
fi

# Verificar se é root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Executando como root. Continuando..."
else
    echo "ℹ️  Executando como usuário normal. Alguns comandos podem precisar de sudo."
fi

# Verificar Python
echo "[1/8] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Instalando Python..."
    if command -v zypper &> /dev/null; then
        # SUSE Linux Enterprise ou openSUSE
        sudo zypper refresh
        sudo zypper install -y python3 python3-pip python3-venv
    elif command -v yast &> /dev/null; then
        # SUSE Linux Enterprise
        sudo yast --install python3 python3-pip python3-venv
    else
        echo "❌ Gerenciador de pacotes SUSE não encontrado!"
        exit 1
    fi
else
    echo "✅ Python já instalado: $(python3 --version)"
fi

# Verificar Git
echo "[2/8] Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "Instalando Git..."
    if command -v zypper &> /dev/null; then
        sudo zypper install -y git
    elif command -v yast &> /dev/null; then
        sudo yast --install git
    fi
else
    echo "✅ Git já instalado: $(git --version)"
fi

# Verificar curl (para testes de conectividade)
echo "[3/8] Verificando curl..."
if ! command -v curl &> /dev/null; then
    echo "Instalando curl..."
    if command -v zypper &> /dev/null; then
        sudo zypper install -y curl
    elif command -v yast &> /dev/null; then
        sudo yast --install curl
    fi
else
    echo "✅ curl já instalado"
fi

# Criar ambiente virtual
echo "[4/8] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Falha ao criar ambiente virtual!"
    exit 1
fi

# Ativar ambiente virtual
echo "[5/8] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Falha ao ativar ambiente virtual!"
    exit 1
fi

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "[6/8] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependencias!"
    exit 1
fi

# Configurar banco
echo "[7/8] Configurando banco de dados..."
python quick_setup.py setup
if [ $? -ne 0 ]; then
    echo "❌ Falha na configuracao do banco!"
    exit 1
fi

# Verificar status
echo "[8/8] Verificando status do sistema..."
python manage_db.py status
if [ $? -ne 0 ]; then
    echo "❌ Falha na verificacao do status!"
    exit 1
fi

# Configurar firewall SUSE
echo "Configurando firewall..."
if command -v firewall-cmd &> /dev/null; then
    # firewalld (SUSE Linux Enterprise 15+)
    sudo firewall-cmd --permanent --add-port=5000/tcp
    sudo firewall-cmd --reload
    echo "✅ Firewall configurado (firewalld)"
elif command -v SuSEfirewall2 &> /dev/null; then
    # SuSEfirewall2 (SUSE Linux Enterprise 12)
    sudo SuSEfirewall2 open EXT TCP 5000
    sudo SuSEfirewall2 start
    echo "✅ Firewall configurado (SuSEfirewall2)"
else
    echo "⚠️  Firewall não detectado. Configure manualmente a porta 5000."
fi

# Iniciar aplicação
echo
echo "========================================"
echo "    CONFIGURACAO SUSE CONCLUIDA!"
echo "========================================"
echo
echo "Acesse: http://localhost:5000"
echo "Usuario admin: admin"
echo "Senha: (a que voce definiu)"
echo
echo "Para parar: Ctrl+C"
echo "Para reiniciar: python app.py"
echo
echo "📋 COMANDOS ÚTEIS SUSE:"
echo "  - Verificar serviços: systemctl status"
echo "  - Verificar firewall: firewall-cmd --list-all"
echo "  - Verificar logs: journalctl -f"
echo "  - Reiniciar rede: systemctl restart network"
echo
python app.py 