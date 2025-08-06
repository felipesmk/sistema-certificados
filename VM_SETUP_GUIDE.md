# 🖥️ Guia de Configuração em VM

## 📋 Pré-requisitos da VM

### **Sistema Operacional Recomendado:**
- **Windows Server 2019/2022** ou **Windows 10/11 Pro**
- **Ubuntu 20.04/22.04 LTS** (alternativa Linux)
- **Mínimo:** 2GB RAM, 20GB HD, 2 vCPUs
- **Recomendado:** 4GB RAM, 50GB HD, 4 vCPUs

### **Software Necessário:**
- Python 3.8+ (ou 3.11+ recomendado)
- Git
- Visual Studio Code (opcional, para edição)
- Navegador web (Chrome, Firefox, Edge)

---

## 🚀 Configuração Automática (Windows)

### **1. Script de Automação Completa**

Crie o arquivo `setup_vm.bat` na raiz do projeto:

```batch
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
```

### **2. Script de Configuração Rápida**

Crie o arquivo `quick_vm_setup.bat`:

```batch
@echo off
echo Configurando VM rapidamente...
call venv\Scripts\activate.bat
pip install -r requirements.txt
python quick_setup.py setup
echo.
echo Pronto! Execute: python app.py
```

---

## 🐧 Configuração Linux (Ubuntu)

### **1. Script de Automação Linux**

Crie o arquivo `setup_vm.sh`:

```bash
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
```

### **2. Tornar Executável e Executar:**

```bash
chmod +x setup_vm.sh
./setup_vm.sh
```

---

## 🔧 Configuração Manual (Passo a Passo)

### **Windows:**

1. **Instalar Python:**
   ```cmd
   # Baixar de https://python.org
   # Marcar "Add to PATH" durante instalação
   ```

2. **Instalar Git:**
   ```cmd
   # Baixar de https://git-scm.com
   ```

3. **Clonar Projeto:**
   ```cmd
   git clone https://github.com/felipesmk/sistema-certificados.git
   cd sistema-certificados
   ```

4. **Configurar Ambiente:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Configurar Sistema:**
   ```cmd
   python quick_setup.py setup
   ```

6. **Executar:**
   ```cmd
   python app.py
   ```

### **Linux:**

1. **Instalar Dependências:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git
   ```

2. **Clonar e Configurar:**
   ```bash
   git clone https://github.com/felipesmk/sistema-certificados.git
   cd sistema-certificados
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configurar Sistema:**
   ```bash
   python quick_setup.py setup
   ```

4. **Executar:**
   ```bash
   python app.py
   ```

---

## 🌐 Configuração de Rede

### **Acesso Local:**
- **Padrão:** `http://localhost:5000`
- **Rede local:** `http://[IP-VM]:5000`

### **Descobrir IP da VM:**

**Windows:**
```cmd
ipconfig
```

**Linux:**
```bash
ip addr show
# ou
hostname -I
```

### **Configurar Firewall:**

**Windows:**
```cmd
# Permitir porta 5000
netsh advfirewall firewall add rule name="Sistema Certificados" dir=in action=allow protocol=TCP localport=5000
```

**Linux:**
```bash
# Permitir porta 5000
sudo ufw allow 5000
```

---

## 🔒 Configuração de Segurança

### **1. Usuário Dedicado (Recomendado):**

**Windows:**
```cmd
# Criar usuário
net user sistema-certificados /add
net localgroup administrators sistema-certificados /add
```

**Linux:**
```bash
# Criar usuário
sudo adduser sistema-certificados
sudo usermod -aG sudo sistema-certificados
```

### **2. Configurar como Serviço:**

**Windows (usando NSSM):**
```cmd
# Instalar NSSM
# nssm install SistemaCertificados "C:\caminho\para\python.exe" "C:\caminho\para\app.py"
# nssm set SistemaCertificados AppDirectory "C:\caminho\para\projeto"
# nssm start SistemaCertificados
```

**Linux (usando systemd):**
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/sistema-certificados.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=Sistema de Certificados
After=network.target

[Service]
Type=simple
User=sistema-certificados
WorkingDirectory=/home/sistema-certificados/projeto
Environment=PATH=/home/sistema-certificados/projeto/venv/bin
ExecStart=/home/sistema-certificados/projeto/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl enable sistema-certificados
sudo systemctl start sistema-certificados
```

---

## 🧪 Testes na VM

### **1. Testes Básicos:**

```bash
# Verificar status
python manage_db.py status

# Testar funcionalidades
python quick_setup.py test-user-features

# Verificar logs
tail -f logs/app.log
```

### **2. Testes de Rede:**

```bash
# Testar conectividade
curl http://localhost:5000

# Testar de outra máquina
curl http://[IP-VM]:5000
```

### **3. Testes de Performance:**

```bash
# Monitorar recursos
htop  # Linux
taskmgr  # Windows

# Testar com múltiplos usuários
# Usar ferramentas como Apache Bench
```

---

## 📊 Monitoramento

### **1. Logs do Sistema:**

**Windows:**
```cmd
# Visualizar logs
type logs\app.log

# Monitorar em tempo real
powershell "Get-Content logs\app.log -Wait"
```

**Linux:**
```bash
# Visualizar logs
tail -f logs/app.log

# Monitorar erros
grep ERROR logs/app.log
```

### **2. Backup Automático:**

**Windows (Task Scheduler):**
```cmd
# Criar tarefa para backup diário
schtasks /create /tn "Backup Sistema" /tr "python manage_db.py backup" /sc daily /st 02:00
```

**Linux (Cron):**
```bash
# Adicionar ao crontab
crontab -e

# Backup diário às 2h
0 2 * * * cd /home/sistema-certificados/projeto && python manage_db.py backup
```

---

## 🚨 Solução de Problemas

### **Problemas Comuns:**

1. **Porta 5000 em uso:**
   ```bash
   # Verificar processos
   netstat -ano | findstr :5000  # Windows
   lsof -i :5000  # Linux
   
   # Matar processo
   taskkill /PID [PID]  # Windows
   kill [PID]  # Linux
   ```

2. **Permissões de arquivo:**
   ```bash
   # Linux
   chmod -R 755 .
   chown -R sistema-certificados:sistema-certificados .
   ```

3. **Ambiente virtual não ativado:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux
   source venv/bin/activate
   ```

4. **Dependências faltando:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

## 📝 Checklist de Configuração

- [ ] **Sistema Operacional** instalado e atualizado
- [ ] **Python 3.8+** instalado
- [ ] **Git** instalado
- [ ] **Projeto clonado** do repositório
- [ ] **Ambiente virtual** criado e ativado
- [ ] **Dependências** instaladas
- [ ] **Banco de dados** configurado
- [ ] **Usuário admin** criado
- [ ] **Aplicação** iniciada com sucesso
- [ ] **Acesso web** funcionando
- [ ] **Firewall** configurado
- [ ] **Backup** configurado
- [ ] **Monitoramento** configurado

---

## 🎯 Próximos Passos

1. **Testar todas as funcionalidades** na VM
2. **Configurar LDAP** se necessário
3. **Personalizar configurações** específicas
4. **Documentar ambiente** específico da VM
5. **Configurar monitoramento** avançado
6. **Implementar backup** automático
7. **Configurar SSL/HTTPS** para produção

---

**🎉 Agora você tem um guia completo para configurar e testar o projeto em qualquer VM!** 