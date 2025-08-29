# 🍎 Guia de Instalação - macOS

## 📋 Pré-requisitos

### **Versões Suportadas:**
- ✅ **macOS 10.15 (Catalina)** ou superior
- ✅ **macOS 11 (Big Sur)** ou superior
- ✅ **macOS 12 (Monterey)** ou superior
- ✅ **macOS 13 (Ventura)** ou superior
- ✅ **macOS 14 (Sonoma)** ou superior

### **Requisitos de Sistema:**
- **RAM:** Mínimo 4GB (recomendado 8GB+)
- **Espaço:** Mínimo 2GB livres
- **Arquitetura:** Intel ou Apple Silicon (M1/M2)

---

## 🚀 Instalação Rápida (Recomendado)

### **Opção 1: Script Automático**
```bash
# Executar script de automação
python quick_setup.py
```

**O que o script faz automaticamente:**
- ✅ Verifica Python e Git
- ✅ Cria ambiente virtual
- ✅ Instala dependências
- ✅ Configura PostgreSQL
- ✅ Configura firewall
- ✅ Inicia aplicação

---

## 📦 Instalação Manual (Passo a Passo)

### **Passo 1: Instalar Homebrew**

```bash
# Instalar Homebrew (gerenciador de pacotes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Adicionar Homebrew ao PATH (se necessário)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### **Passo 2: Instalar Dependências do Sistema**

```bash
# Atualizar Homebrew
brew update

# Instalar Python, Git e outras dependências
brew install python@3.11 git curl

# Verificar instalação
python3 --version
git --version
```

### **Passo 3: Clonar o Repositório**

```bash
# Clonar o projeto
git clone https://github.com/felipesmk/sistema-certificados.git
cd sistema-certificados
```

### **Passo 4: Criar Ambiente Virtual**

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se está ativo (deve mostrar o caminho do venv)
which python
```

### **Passo 5: Instalar Dependências Python**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### **Passo 6: Instalar e Configurar PostgreSQL**

#### **Opção A: PostgreSQL via Homebrew (Recomendado)**

```bash
# Instalar PostgreSQL
brew install postgresql@15

# Iniciar PostgreSQL
brew services start postgresql@15

# Adicionar ao PATH (se necessário)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

#### **Opção B: PostgreSQL via Docker**

```bash
# Instalar Docker Desktop
# Baixe de: https://www.docker.com/products/docker-desktop/

# Subir PostgreSQL
docker-compose up -d postgres
```

### **Passo 7: Configurar PostgreSQL**

```bash
# Configurar via script interativo
python configure_postgresql.py
```

### **Passo 8: Configurar Banco de Dados**

```bash
# Setup completo automático
python quick_setup.py setup

# OU configuração manual
python manage_db.py migrate
python manage_db.py create-admin
```

### **Passo 9: Configurar Firewall**

```bash
# macOS tem firewall integrado, mas pode ser necessário configurar
# Vá em: Sistema > Preferências do Sistema > Segurança e Privacidade > Firewall

# OU via linha de comando (se disponível)
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /usr/bin/python3
```

### **Passo 10: Iniciar Aplicação**

```bash
# Desenvolvimento
python app.py

# OU produção
python run_production.py
```

### **Passo 11: Acessar Sistema**

- **Desenvolvimento:** http://localhost:5000
- **Produção:** http://localhost
- **Usuário:** admin
- **Senha:** (definida durante setup)

---

## 🔧 Configuração Avançada

### **Configurar Email (Opcional)**

1. **Editar arquivo .env:**
   ```bash
   # Usando nano
   nano .env
   
   # OU usando vim
   vim .env
   
   # OU usando TextEdit
   open -e .env
   ```

2. **Configurar SMTP:**
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=seu_email@gmail.com
   MAIL_PASSWORD=sua_senha_de_app
   MAIL_DEFAULT_SENDER=seu_email@gmail.com
   ```

### **Configurar LDAP (Opcional)**

1. **Editar arquivo .env:**
   ```env
   AUTH_MODE=ldap
   LDAP_SERVER=ldap://seu-servidor-ldap.com
   LDAP_PORT=389
   LDAP_BASE_DN=dc=exemplo,dc=com
   LDAP_USER_DN=ou=usuarios
   LDAP_USER_ATTR=sAMAccountName
   LDAP_BIND_DN=cn=admin,dc=exemplo,dc=com
   LDAP_BIND_PASSWORD=sua_senha_ldap
   ```

2. **Executar migração:**
   ```bash
   python manage_db.py migrate
   ```

### **Configurar como Serviço (Opcional)**

1. **Instalar launchd (já incluído no macOS):**
   ```bash
   # Criar arquivo de serviço
   nano ~/Library/LaunchAgents/com.sistema.certificados.plist
   ```

2. **Conteúdo do arquivo:**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.sistema.certificados</string>
       <key>ProgramArguments</key>
       <array>
           <string>/caminho/para/sistema-certificados/venv/bin/python</string>
           <string>/caminho/para/sistema-certificados/run_production.py</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/caminho/para/sistema-certificados</string>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```

3. **Carregar e iniciar serviço:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.sistema.certificados.plist
   launchctl start com.sistema.certificados
   ```

---

## 🛠️ Comandos Úteis

### **Gerenciamento do Sistema**
```bash
# Verificar status
python manage_db.py status

# Backup do banco
python manage_db.py backup

# Restaurar backup
python manage_db.py restore

# Criar usuário adicional
python manage_db.py create-user

# Resetar banco (CUIDADO!)
python manage_db.py reset --force
```

### **Desenvolvimento**
```bash
# Executar testes
python test_validation.py
python test_vm_installation.py

# Verificar logs
tail -f logs/app.log

# Parar aplicação
Ctrl+C
```

### **Produção**
```bash
# Instalar dependências de produção
python quick_setup.py install-prod

# Executar em produção
python run_production.py

# OU usar Gunicorn diretamente
gunicorn -c gunicorn.conf.py app:app
```

### **Gerenciamento de Serviços**
```bash
# Verificar status do PostgreSQL
brew services list | grep postgresql

# Reiniciar PostgreSQL
brew services restart postgresql@15

# Parar PostgreSQL
brew services stop postgresql@15
```

---

## 🔍 Solução de Problemas

### **Problema: Python não encontrado**
```bash
# Verificar versão do Python
python3 --version

# Se não funcionar, reinstale via Homebrew
brew install python@3.11
```

### **Problema: Porta em uso**
```bash
# Verificar portas em uso
lsof -i :5000
lsof -i :80

# Matar processo na porta
kill -9 <PID>
```

### **Problema: PostgreSQL não conecta**
```bash
# Verificar se PostgreSQL está rodando
brew services list | grep postgresql

# Iniciar PostgreSQL
brew services start postgresql@15

# Verificar logs
tail -f /opt/homebrew/var/log/postgresql@15.log
```

### **Problema: Permissões**
```bash
# Verificar permissões
ls -la

# Executar setup
python quick_setup.py
```

### **Problema: Dependências não instalam**
```bash
# Atualizar pip
pip install --upgrade pip

# Limpar cache
pip cache purge

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### **Problema: Ambiente virtual corrompido**
```bash
# Remover venv
rm -rf venv

# Recriar ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Problema: Homebrew não encontrado**
```bash
# Reinstalar Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Adicionar ao PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
source ~/.zprofile
```

---

## 📞 Suporte

### **Logs Importantes**
- **Aplicação:** `logs/app.log`
- **Sistema:** Console.app
- **PostgreSQL:** `/opt/homebrew/var/log/postgresql@15.log`

### **Verificar Status Completo**
```bash
python quick_setup.py status
```

### **Informações do Sistema**
```bash
# Versão do macOS
sw_vers

# Arquitetura
uname -m

# Versão do Python
python3 --version

# Versão do pip
pip3 --version

# Espaço em disco
df -h

# Memória
vm_stat
```

### **Comandos de Diagnóstico**
```bash
# Verificar conectividade
ping -c 4 google.com

# Verificar portas abertas
lsof -i -P | grep LISTEN

# Verificar processos Python
ps aux | grep python

# Verificar uso de memória
top -l 1 | head -n 10
```

---

## ✅ Checklist de Instalação

- [ ] Homebrew instalado
- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] PostgreSQL instalado e configurado
- [ ] Banco de dados inicializado
- [ ] Firewall configurado (se necessário)
- [ ] Aplicação iniciada
- [ ] Sistema acessível via navegador
- [ ] Usuário admin criado
- [ ] Email configurado (opcional)
- [ ] LDAP configurado (opcional)
- [ ] Serviço configurado (opcional)

---

## 🍎 Características Específicas do macOS

### **Vantagens:**
- ✅ **Python pré-instalado** (mas pode ser antigo)
- ✅ **Git pré-instalado** (mas pode ser antigo)
- ✅ **Terminal Unix-like** (compatível com comandos Linux)
- ✅ **Homebrew** (excelente gerenciador de pacotes)
- ✅ **Docker Desktop** (fácil instalação)

### **Considerações:**
- ⚠️ **Firewall integrado** (pode bloquear conexões)
- ⚠️ **Permissões de aplicações** (Gatekeeper)
- ⚠️ **Atualizações automáticas** (podem quebrar dependências)

### **Dicas:**
- Use **Homebrew** para instalar software
- Configure **permissões de aplicações** se necessário
- Use **Docker** para PostgreSQL se tiver problemas com instalação local
- Mantenha o **sistema atualizado**

---

## 🚀 Alternativas de Instalação

### **Usando Docker (Recomendado para desenvolvimento)**

```bash
# Instalar Docker Desktop
# Baixe de: https://www.docker.com/products/docker-desktop/

# Clonar repositório
git clone https://github.com/felipesmk/sistema-certificados.git
cd sistema-certificados

# Subir serviços
docker-compose up -d

# Configurar banco
python configure_postgresql.py
python quick_setup.py setup
```

### **Usando Conda (Alternativo)**

```bash
# Instalar Miniconda
# Baixe de: https://docs.conda.io/en/latest/miniconda.html

# Criar ambiente
conda create -n sistema-certificados python=3.11
conda activate sistema-certificados

# Instalar dependências
pip install -r requirements.txt
```

---

**🎯 Se todos os itens estiverem marcados, sua instalação está completa!**

Para dúvidas ou problemas, consulte a seção de Solução de Problemas ou abra uma issue no repositório.
