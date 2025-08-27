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
            # Tentar instalar com nomes alternativos se necessário
            if ! sudo zypper install -y python3 python3-pip python3-venv git curl; then
                echo "⚠️  Tentando nomes alternativos de pacotes..."
                sudo zypper install -y python3 python3-pip3 python3-virtualenv git-core curl
            fi
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

# Configurar PostgreSQL
configure_postgresql() {
    echo "🗄️  Configurando PostgreSQL..."
    echo
    
    # Verificar se PostgreSQL está instalado
    if ! command -v psql &> /dev/null; then
        echo "📦 Instalando PostgreSQL..."
        case $1 in
            "ubuntu"|"debian")
                sudo apt install -y postgresql postgresql-contrib
                ;;
            "opensuse"|"sles"|"suse")
                sudo zypper install -y postgresql postgresql-server
                ;;
            "centos"|"rhel"|"fedora")
                sudo dnf install -y postgresql postgresql-server
                ;;
        esac
    fi
    
    # Inicializar PostgreSQL se necessário
    if [ ! -d "/var/lib/pgsql/data" ] && [ ! -d "/var/lib/postgresql/data" ]; then
        echo "🔧 Inicializando PostgreSQL..."
        sudo postgresql-setup initdb
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
    fi
    
    echo "🔐 Configurando credenciais do banco..."
    echo "Por favor, defina as credenciais para o banco de dados:"
    echo
    
    read -p "Nome do usuário PostgreSQL (padrão: certificados_user): " DB_USER
    DB_USER=${DB_USER:-certificados_user}
    
    read -s -p "Senha do usuário PostgreSQL: " DB_PASSWORD
    echo
    
    read -p "Nome do banco de dados (padrão: certificados_db): " DB_NAME
    DB_NAME=${DB_NAME:-certificados_db}
    
    read -p "Host PostgreSQL (padrão: localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Porta PostgreSQL (padrão: 5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    # Criar usuário e banco
    echo "🔧 Criando usuário e banco de dados..."
    sudo -u postgres psql << EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME OWNER $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF
    
    # Configurar autenticação
    echo "🔧 Configurando autenticação..."
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/data/postgresql.conf
    
    # Configurar pg_hba.conf para permitir conexões locais
    echo "local $DB_NAME $DB_USER md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
    
    # Reiniciar PostgreSQL
    sudo systemctl restart postgresql
    
    # Criar arquivo .env com as credenciais
    echo "📝 Criando arquivo .env..."
    cat > .env << EOF
# Configurações do Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$(openssl rand -hex 32)

# Configurações do Banco de Dados PostgreSQL
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# Configurações de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app
MAIL_DEFAULT_SENDER=seu_email@gmail.com

# Configurações de Autenticação
AUTH_MODE=banco

# Configurações de Sessão
PERMANENT_SESSION_LIFETIME=3600

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Configurações do Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=America/Sao_Paulo
EOF
    
    echo "✅ PostgreSQL configurado com sucesso!"
    echo "📋 Credenciais salvas em .env"
    echo "🔐 DATABASE_URL: postgresql://$DB_USER:***@$DB_HOST:$DB_PORT/$DB_NAME"
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
echo "[1/10] Verificando Python..."
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
echo "[2/10] Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "❌ Git não encontrado! Execute o script novamente."
    exit 1
else
    echo "✅ Git já instalado: $(git --version)"
fi

# Criar ambiente virtual
echo "[3/10] Criando ambiente virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Falha ao criar ambiente virtual!"
    exit 1
fi

# Ativar ambiente virtual
echo "[4/10] Ativando ambiente virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Falha ao ativar ambiente virtual!"
    exit 1
fi

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "[5/10] Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependencias!"
    exit 1
fi

# Configurar PostgreSQL
echo "[6/10] Configurando PostgreSQL..."
configure_postgresql $DISTRO_ID
if [ $? -ne 0 ]; then
    echo "❌ Falha na configuracao do PostgreSQL!"
    exit 1
fi

# Configurar banco
echo "[7/10] Configurando banco de dados..."
python quick_setup.py setup
if [ $? -ne 0 ]; then
    echo "❌ Falha na configuracao do banco!"
    exit 1
fi

# Verificar status
echo "[8/10] Verificando status do sistema..."
python manage_db.py status
if [ $? -ne 0 ]; then
    echo "❌ Falha na verificacao do status!"
    exit 1
fi

# Configurar firewall
echo "[9/10] Configurando firewall..."
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