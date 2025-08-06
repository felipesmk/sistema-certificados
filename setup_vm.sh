#!/bin/bash

echo "========================================"
echo "    CONFIGURACAO AUTOMATICA DA VM"
echo "========================================"
echo

# Verificar Python
echo "[1/8] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Instalando Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Verificar Git
echo "[2/8] Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "Instalando Git..."
    sudo apt install -y git
fi

# Criar ambiente virtual
echo "[3/8] Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "[4/8] Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "[5/8] Instalando dependencias..."
pip install -r requirements.txt

# Configurar banco
echo "[6/8] Configurando banco de dados..."
python quick_setup.py setup

# Verificar status
echo "[7/8] Verificando status do sistema..."
python manage_db.py status

# Iniciar aplicação
echo "[8/8] Iniciando aplicacao..."
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
python app.py 