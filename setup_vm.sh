#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO AUTOMATICA VM LINUX"
echo "========================================"
echo

# Detectar distribuição Linux
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "Sistema detectado: $PRETTY_NAME"
        echo "Versão: $VERSION"
        echo "ID: $ID"
        echo
        return 0
    else
        echo "❌ Não foi possível detectar a distribuição Linux"
        return 1
    fi
}

# Instalar dependências baseado na distribuição
install_dependencies() {
    local distro=$1
    
    case $distro in
        "ubuntu"|"debian")
            echo "📦 Instalando dependências (Ubuntu/Debian)..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl
            ;;
        "opensuse"|"sles"|"suse")
            echo "📦 Instalando dependências (SUSE)..."
            sudo zypper refresh
            sudo zypper install -y python3 python3-pip python3-venv git curl
            ;;
        "centos"|"rhel"|"fedora")
            echo "📦 Instalando dependências (Red Hat/Fedora)..."
            sudo dnf install -y python3 python3-pip python3-venv git curl
            ;;
        *)
            echo "⚠️  Distribuição não suportada: $distro"
            echo "Instale manualmente: python3, python3-pip, python3-venv, git, curl"
            return 1
            ;;
    esac
}

# Configurar firewall baseado na distribuição
configure_firewall() {
    local distro=$1
    
    echo "🔥 Configurando firewall..."
    
    case $distro in
        "ubuntu"|"debian")
            if command -v ufw &> /dev/null; then
                sudo ufw allow 5000
                echo "✅ Firewall UFW configurado"
            else
                echo "⚠️  UFW não encontrado, configure manualmente a porta 5000"
            fi
            ;;
        "opensuse"|"sles"|"suse")
            if command -v firewall-cmd &> /dev/null; then
                sudo firewall-cmd --permanent --add-port=5000/tcp
                sudo firewall-cmd --reload
                echo "✅ Firewall firewalld configurado"
            elif command -v SuSEfirewall2 &> /dev/null; then
                sudo SuSEfirewall2 open EXT TCP 5000
                sudo SuSEfirewall2 start
                echo "✅ Firewall SuSEfirewall2 configurado"
            else
                echo "⚠️  Firewall não encontrado, configure manualmente a porta 5000"
            fi
            ;;
        "centos"|"rhel"|"fedora")
            if command -v firewall-cmd &> /dev/null; then
                sudo firewall-cmd --permanent --add-port=5000/tcp
                sudo firewall-cmd --reload
                echo "✅ Firewall firewalld configurado"
            else
                echo "⚠️  Firewall não encontrado, configure manualmente a porta 5000"
            fi
            ;;
    esac
}

# Verificar se é root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Executando como root. Continuando..."
else
    echo "ℹ️  Executando como usuário normal. Alguns comandos podem precisar de sudo."
fi

# Detectar distribuição
if ! detect_distro; then
    exit 1
fi

# Extrair ID da distribuição
. /etc/os-release
DISTRO_ID=$ID

# Verificar Python
echo "[1/8] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Instalando Python..."
    if ! install_dependencies $DISTRO_ID; then
        echo "❌ Falha ao instalar dependências!"
        exit 1
    fi
else
    echo "✅ Python já instalado: $(python3 --version)"
fi

# Verificar Git
echo "[2/8] Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "❌ Git não encontrado! Execute o script novamente."
    exit 1
else
    echo "✅ Git já instalado: $(git --version)"
fi

# Criar ambiente virtual
echo "[3/8] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Falha ao criar ambiente virtual!"
    exit 1
fi

# Ativar ambiente virtual
echo "[4/8] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Falha ao ativar ambiente virtual!"
    exit 1
fi

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "[5/8] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependencias!"
    exit 1
fi

# Configurar banco
echo "[6/8] Configurando banco de dados..."
python quick_setup.py setup
if [ $? -ne 0 ]; then
    echo "❌ Falha na configuracao do banco!"
    exit 1
fi

# Verificar status
echo "[7/8] Verificando status do sistema..."
python manage_db.py status
if [ $? -ne 0 ]; then
    echo "❌ Falha na verificacao do status!"
    exit 1
fi

# Configurar firewall
echo "[8/8] Configurando firewall..."
configure_firewall $DISTRO_ID

# Iniciar aplicação
echo
echo "========================================"
echo "    CONFIGURACAO CONCLUIDA!"
echo "========================================"
echo
echo "Acesse: http://localhost:5000"
echo "Usuario admin: admin"
echo "Senha: (a que voce definiu)"
echo
echo "Para parar: Ctrl+C"
echo "Para reiniciar: python app.py"
echo
echo "📋 COMANDOS ÚTEIS:"
echo "  - Verificar serviços: systemctl status"
echo "  - Verificar logs: journalctl -f"
echo "  - Testar conectividade: curl http://localhost:5000"
echo
python app.py 