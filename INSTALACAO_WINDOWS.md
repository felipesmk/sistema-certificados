# 🖥️ Guia de Instalação - Windows

## 📋 Pré-requisitos

### **Software Necessário:**
- **Windows 10/11** (64-bit)
- **Python 3.8+** (recomendado 3.11+)
- **Git** para Windows
- **PostgreSQL** (opcional - pode usar Docker)

### **Requisitos de Sistema:**
- **RAM:** Mínimo 4GB (recomendado 8GB+)
- **Espaço:** Mínimo 2GB livres
- **Permissões:** Acesso de administrador (para firewall)

---

## 🚀 Instalação Rápida (Recomendado)

### **Opção 1: Script Automático**
```batch
# Execute o script de automação
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

### **Passo 1: Instalar Python**

1. **Baixe Python:**
   - Acesse: https://www.python.org/downloads/
   - Baixe a versão mais recente (3.11+)
   - **IMPORTANTE:** Marque "Add Python to PATH"

2. **Verificar instalação:**
   ```batch
   python --version
   pip --version
   ```

### **Passo 2: Instalar Git**

1. **Baixe Git:**
   - Acesse: https://git-scm.com/download/win
   - Baixe e instale com configurações padrão

2. **Verificar instalação:**
   ```batch
   git --version
   ```

### **Passo 3: Clonar o Repositório**

```batch
# Abra o PowerShell ou CMD como administrador
git clone https://github.com/felipesmk/sistema-certificados.git
cd sistema-certificados
```

### **Passo 4: Criar Ambiente Virtual**

```batch
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate

# Verificar se está ativo (deve mostrar o caminho do venv)
where python
```

### **Passo 5: Instalar Dependências**

```batch
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### **Passo 6: Configurar PostgreSQL**

#### **Opção A: PostgreSQL Local (Recomendado)**

1. **Baixar PostgreSQL:**
   - Acesse: https://www.postgresql.org/download/windows/
   - Ou: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Baixe a versão mais recente

2. **Instalar PostgreSQL:**
   - Execute o instalador
   - Defina senha para usuário `postgres`
   - Mantenha porta padrão (5432)
   - Instale pgAdmin (opcional)

3. **Configurar via script:**
   ```batch
   python configure_postgresql.py
   ```

#### **Opção B: Docker (Alternativo)**

1. **Instalar Docker Desktop:**
   - Baixe: https://www.docker.com/products/docker-desktop/
   - Instale e reinicie o computador

2. **Subir PostgreSQL:**
   ```batch
   docker-compose up -d postgres
   ```

3. **Configurar via script:**
   ```batch
   python configure_postgresql.py
   ```

### **Passo 7: Configurar Banco de Dados**

```batch
# Setup completo automático
python quick_setup.py setup

# OU configuração manual
python manage_db.py migrate
python manage_db.py create-admin
```

### **Passo 8: Configurar Firewall**

```batch
# Desenvolvimento (porta 5000)
netsh advfirewall firewall add rule name="Sistema Certificados Dev" dir=in action=allow protocol=TCP localport=5000

# Produção (porta 80)
netsh advfirewall firewall add rule name="Sistema Certificados Prod" dir=in action=allow protocol=TCP localport=80
```

### **Passo 9: Iniciar Aplicação**

```batch
# Desenvolvimento
python app.py

# OU produção
python run_production.py
```

### **Passo 10: Acessar Sistema**

- **Desenvolvimento:** http://localhost:5000
- **Produção:** http://localhost
- **Usuário:** admin
- **Senha:** (definida durante setup)

---

## 🔧 Configuração Avançada

### **Configurar Email (Opcional)**

1. **Editar arquivo .env:**
   ```batch
   notepad .env
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
   ```batch
   python manage_db.py migrate
   ```

---

## 🛠️ Comandos Úteis

### **Gerenciamento do Sistema**
```batch
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
```batch
# Executar testes
python test_validation.py
python test_vm_installation.py

# Verificar logs
type logs\app.log

# Parar aplicação
Ctrl+C
```

### **Produção**
```batch
# Instalar dependências de produção
python quick_setup.py install-prod

# Executar em produção
python run_production.py

# OU usar Waitress diretamente
waitress-serve --host=0.0.0.0 --port=80 app:app
```

---

## 🔍 Solução de Problemas

### **Problema: Python não encontrado**
```batch
# Verificar se Python está no PATH
python --version

# Se não funcionar, reinstale Python marcando "Add to PATH"
```

### **Problema: Porta em uso**
```batch
# Verificar portas em uso
netstat -an | findstr 5000
netstat -an | findstr 80

# Matar processo na porta
taskkill /PID <PID> /F
```

### **Problema: PostgreSQL não conecta**
```batch
# Verificar se PostgreSQL está rodando
services.msc
# Procure por "postgresql" e inicie o serviço

# OU via linha de comando
net start postgresql
```

### **Problema: Firewall bloqueando**
```batch
# Verificar regras do firewall
netsh advfirewall firewall show rule name="Sistema Certificados*"

# Remover e recriar regras
netsh advfirewall firewall delete rule name="Sistema Certificados Dev"
netsh advfirewall firewall delete rule name="Sistema Certificados Prod"
# Recriar conforme Passo 8
```

### **Problema: Dependências não instalam**
```batch
# Atualizar pip
python -m pip install --upgrade pip

# Limpar cache
pip cache purge

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### **Problema: Ambiente virtual corrompido**
```batch
# Remover venv
rmdir /s venv

# Recriar ambiente virtual
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📞 Suporte

### **Logs Importantes**
- **Aplicação:** `logs\app.log`
- **Sistema:** Event Viewer > Windows Logs > Application

### **Verificar Status Completo**
```batch
python test_vm_installation.py
```

### **Informações do Sistema**
```batch
# Versão do Windows
ver

# Informações do sistema
systeminfo

# Versão do Python
python --version

# Versão do pip
pip --version
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] PostgreSQL configurado
- [ ] Banco de dados inicializado
- [ ] Firewall configurado
- [ ] Aplicação iniciada
- [ ] Sistema acessível via navegador
- [ ] Usuário admin criado
- [ ] Email configurado (opcional)
- [ ] LDAP configurado (opcional)

---

**🎯 Se todos os itens estiverem marcados, sua instalação está completa!**

Para dúvidas ou problemas, consulte a seção de Solução de Problemas ou abra uma issue no repositório.
