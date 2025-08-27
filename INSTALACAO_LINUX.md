# 🐧 Guia de Instalação - Linux

## 📋 Pré-requisitos

### **Distribuições Suportadas:**
- ✅ **Ubuntu** 20.04+ / **Debian** 11+
- ✅ **SUSE Linux Enterprise** / **openSUSE** 15+
- ✅ **CentOS** 8+ / **RHEL** 8+ / **Fedora** 35+
- ✅ **Outras distribuições** baseadas nas acima

### **Requisitos de Sistema:**
- **RAM:** Mínimo 4GB (recomendado 8GB+)
- **Espaço:** Mínimo 2GB livres
- **Permissões:** Acesso sudo

---

## 🚀 Instalação Rápida (Recomendado)

### **Opção 1: Script Automático**
```bash
# Dar permissão de execução
chmod +x setup_vm.sh

# Executar script de automação
./setup_vm.sh
```

**O que o script faz automaticamente:**
- ✅ Detecta distribuição automaticamente
- ✅ Instala Python, pip, venv, git
- ✅ Cria ambiente virtual
- ✅ Instala dependências
- ✅ Instala e configura PostgreSQL
- ✅ Configura firewall
- ✅ Inicia aplicação

---

## 📦 Instalação Manual (Passo a Passo)

### **Passo 1: Atualizar Sistema**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# SUSE
sudo zypper refresh && sudo zypper update -y

# CentOS/RHEL/Fedora
sudo dnf update -y
```

### **Passo 2: Instalar Dependências do Sistema**

#### **Ubuntu/Debian:**
```bash
sudo apt install -y python3 python3-pip python3-venv git curl
```

#### **SUSE:**
```bash
sudo zypper install -y python3 python3-pip python3-virtualenv git-core curl
```

#### **CentOS/RHEL/Fedora:**
```bash
sudo dnf install -y python3 python3-pip python3-virtualenv git curl
```

### **Passo 3: Verificar Instalação**

```bash
python3 --version
pip3 --version
git --version
```

### **Passo 4: Clonar o Repositório**

```bash
git clone https://github.com/felipesmk/sistema-certificados.git
cd sistema-certificados
```

### **Passo 5: Criar Ambiente Virtual**

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se está ativo (deve mostrar o caminho do venv)
which python
```

### **Passo 6: Instalar Dependências Python**

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

### **Passo 7: Instalar e Configurar PostgreSQL**

#### **Ubuntu/Debian:**
```bash
# Instalar PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Inicializar banco
sudo postgresql-setup initdb

# Habilitar e iniciar serviço
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### **SUSE:**
```bash
# Instalar PostgreSQL
sudo zypper install -y postgresql postgresql-server

# Inicializar banco
sudo postgresql-setup initdb

# Habilitar e iniciar serviço
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### **CentOS/RHEL/Fedora:**
```bash
# Instalar PostgreSQL
sudo dnf install -y postgresql postgresql-server

# Inicializar banco
sudo postgresql-setup initdb

# Habilitar e iniciar serviço
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### **Passo 8: Configurar PostgreSQL**

```bash
# Configurar via script interativo
python configure_postgresql.py
```

### **Passo 9: Configurar Banco de Dados**

```bash
# Setup completo automático
python quick_setup.py setup

# OU configuração manual
python manage_db.py migrate
python manage_db.py create-admin
```

### **Passo 10: Configurar Firewall**

#### **Ubuntu/Debian (UFW):**
```bash
# Instalar UFW se não estiver instalado
sudo apt install -y ufw

# Configurar portas
sudo ufw allow 5000  # Desenvolvimento
sudo ufw allow 80    # Produção
sudo ufw enable
```

#### **SUSE (firewalld/SuSEfirewall2):**
```bash
# Usando firewalld
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload

# OU usando SuSEfirewall2
sudo SuSEfirewall2 open EXT TCP 5000
sudo SuSEfirewall2 open EXT TCP 80
sudo SuSEfirewall2 start
```

#### **CentOS/RHEL/Fedora (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

### **Passo 11: Iniciar Aplicação**

```bash
# Desenvolvimento
python app.py

# OU produção
python run_production.py
```

### **Passo 12: Acessar Sistema**

- **Desenvolvimento:** http://localhost:5000
- **Produção:** http://localhost
- **Usuário:** admin
- **Senha:** (definida durante setup)

---

## 🔧 Configuração Avançada

### **Configurar Email (Opcional)**

1. **Editar arquivo .env:**
   ```bash
   nano .env
   # OU
   vim .env
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

### **Configurar como Serviço do Sistema**

1. **Criar arquivo de serviço:**
   ```bash
   sudo nano /etc/systemd/system/sistema-certificados.service
   ```

2. **Conteúdo do arquivo:**
   ```ini
   [Unit]
   Description=Sistema de Certificados
   After=network.target postgresql.service

   [Service]
   Type=simple
   User=seu_usuario
   WorkingDirectory=/caminho/para/sistema-certificados
   Environment=PATH=/caminho/para/sistema-certificados/venv/bin
   ExecStart=/caminho/para/sistema-certificados/venv/bin/python run_production.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Habilitar e iniciar serviço:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable sistema-certificados
   sudo systemctl start sistema-certificados
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
sudo systemctl status postgresql

# Reiniciar PostgreSQL
sudo systemctl restart postgresql

# Verificar logs do PostgreSQL
sudo journalctl -u postgresql -f
```

---

## 🔍 Solução de Problemas

### **Problema: Python não encontrado**
```bash
# Verificar versão do Python
python3 --version

# Se não funcionar, instale Python
sudo apt install python3  # Ubuntu/Debian
sudo zypper install python3  # SUSE
sudo dnf install python3  # CentOS/RHEL/Fedora
```

### **Problema: Porta em uso**
```bash
# Verificar portas em uso
sudo netstat -tlnp | grep 5000
sudo netstat -tlnp | grep 80

# Matar processo na porta
sudo kill -9 <PID>
```

### **Problema: PostgreSQL não conecta**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql

# Verificar logs
sudo journalctl -u postgresql -f
```

### **Problema: Firewall bloqueando**
```bash
# UFW (Ubuntu/Debian)
sudo ufw status
sudo ufw allow 5000
sudo ufw allow 80

# firewalld (SUSE/CentOS/RHEL/Fedora)
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
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

### **Problema: Permissões**
```bash
# Verificar permissões
ls -la

# Corrigir permissões
chmod +x setup_vm.sh
chmod +x configure_network.sh
```

### **Problema: Autenticação PostgreSQL no SUSE**
Se você encontrar erro de autenticação "Ident" no PostgreSQL no SUSE, execute:

```bash
# 1. Acessar como usuário postgres
sudo -u postgres psql

# 2. No prompt do PostgreSQL, execute:
ALTER SYSTEM SET password_encryption = 'md5';
SELECT pg_reload_conf();
\q

# 3. Editar arquivo de configuração
sudo -u postgres nano /var/lib/pgsql/data/pg_hba.conf

# 4. Substituir linhas com 'ident' por 'md5':
# local   all             all                                     md5
# host    all             all             127.0.0.1/32            md5
# host    all             all             ::1/128                 md5

# 5. Reiniciar PostgreSQL
sudo systemctl restart postgresql

# 6. Testar conexão
python quick_setup.py setup
```

### **Problema: Compatibilidade Python < 3.7 no SUSE**
Se você encontrar erros relacionados a `capture_output` ou `text=True` no subprocess, o sistema detecta automaticamente e usa compatibilidade:

```bash
# Verificar versão do Python
python3 --version

# Se for < 3.7, o sistema usa compatibilidade automática
# Não é necessário fazer nada manualmente
```

### **Problema: Elevação de Privilégios no SUSE (Porta 80)**
No SUSE Linux, ao executar `python run_production.py`, você pode encontrar problemas com privilégios para usar a porta 80. O sistema oferece 3 opções interativas:

```bash
# Executar aplicação
python run_production.py

# Opções que aparecerão:
# 1. Usar porta 8080 (recomendado para desenvolvimento)
# 2. Tentar usar sudo para porta 80
# 3. Configurar sysctl para permitir porta 80 sem privilégios

# Recomendação: Use a opção 1 (porta 8080) para desenvolvimento
# Use a opção 3 para produção (configura permanentemente)
```

**Configuração Permanente para Porta 80 (Opção 3):**
```bash
# O sistema configurará automaticamente:
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee -a /etc/sysctl.conf
```

### **Problema: Erros de Encoding UTF-8**
Se encontrar erros de encoding, todos os scripts já incluem a declaração UTF-8:

```python
# -*- coding: utf-8 -*-
```

**Não é necessário fazer nada manualmente.**

---

## 📞 Suporte

### **Logs Importantes**
- **Aplicação:** `logs/app.log`
- **Sistema:** `journalctl -f`
- **PostgreSQL:** `sudo journalctl -u postgresql -f`

### **Verificar Status Completo**
```bash
python test_vm_installation.py
```

### **Informações do Sistema**
```bash
# Distribuição
cat /etc/os-release

# Versão do kernel
uname -r

# Versão do Python
python3 --version

# Versão do pip
pip3 --version

# Espaço em disco
df -h

# Memória
free -h
```

### **Comandos de Diagnóstico**
```bash
# Verificar conectividade
ping -c 4 google.com

# Verificar portas abertas
sudo netstat -tlnp

# Verificar processos Python
ps aux | grep python

# Verificar uso de memória
htop
```

---

## ✅ Checklist de Instalação

- [ ] Sistema atualizado
- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] PostgreSQL instalado e configurado
- [ ] Banco de dados inicializado
- [ ] Firewall configurado
- [ ] Aplicação iniciada
- [ ] Sistema acessível via navegador
- [ ] Usuário admin criado
- [ ] Email configurado (opcional)
- [ ] LDAP configurado (opcional)
- [ ] Serviço do sistema configurado (opcional)

---

## 🐧 Distribuições Específicas

### **Ubuntu/Debian**
- Usa `apt` como gerenciador de pacotes
- Firewall padrão: UFW
- Serviços gerenciados por systemd

### **SUSE**
- Usa `zypper` como gerenciador de pacotes
- Firewall: firewalld ou SuSEfirewall2
- Serviços gerenciados por systemd
- **Compatibilidade Python:** Detecta automaticamente versões < 3.7
- **Elevação de Privilégios:** Sistema interativo para porta 80
- **PostgreSQL:** Configuração específica para autenticação md5

### **CentOS/RHEL/Fedora**
- Usa `dnf` como gerenciador de pacotes
- Firewall padrão: firewalld
- Serviços gerenciados por systemd

---

## 🔄 Últimas Modificações e Melhorias

### **Compatibilidade Python < 3.7**
- ✅ **Subprocess:** Substituído `capture_output=True, text=True` por compatibilidade universal
- ✅ **F-strings:** Convertido para `.format()` em `run_production.py`
- ✅ **Encoding:** Adicionado `# -*- coding: utf-8 -*-` em todos os scripts

### **SUSE Linux - Soluções Específicas**
- ✅ **PostgreSQL Auth:** Script automático para corrigir autenticação "Ident"
- ✅ **Privilégios Porta 80:** Sistema interativo com 3 opções
- ✅ **Detecção Automática:** Identifica SUSE e aplica configurações específicas

### **SQLAlchemy - Correções de Sessão**
- ✅ **DetachedInstanceError:** Implementado `lazy='select'` e tratamento de erros
- ✅ **to_dict():** Protegido com try-except para evitar erros de sessão
- ✅ **Export/Import:** Melhorado tratamento de relacionamentos

### **Scripts Atualizados**
- ✅ `configure_postgresql.py` - Compatibilidade subprocess
- ✅ `manage_db.py` - Compatibilidade subprocess + encoding
- ✅ `quick_setup.py` - Integração correção PostgreSQL SUSE
- ✅ `run_production.py` - Sistema interativo privilégios + compatibilidade
- ✅ `test_vm_installation.py` - Compatibilidade subprocess
- ✅ `models.py` - Correções SQLAlchemy
- ✅ `app.py` - Melhorias export/import

### **Comandos de Verificação**
```bash
# Testar compatibilidade
python test_vm_installation.py

# Verificar configuração PostgreSQL
python quick_setup.py setup

# Testar aplicação
python run_production.py
```

---

**🎯 Se todos os itens estiverem marcados, sua instalação está completa!**

Para dúvidas ou problemas, consulte a seção de Solução de Problemas ou abra uma issue no repositório.
