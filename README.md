# 🏢 Sistema de Gestão de Certificados e Documentos Controlados

## 📋 Visão Geral

Sistema web completo para gestão de certificados, senhas, licenças e documentos controlados com controle de acesso baseado em perfis (RBAC). Desenvolvido em Flask com interface moderna, dashboards interativos, sistema robusto de validação e funcionalidades avançadas de autenticação e notificação.

## ✨ Funcionalidades Principais

### 🔐 **Segurança e Autenticação**
- **RBAC Completo** - Controle de acesso baseado em perfis e permissões
- **Autenticação Dupla** - Banco de dados ou LDAP/Active Directory
- **Sessões Seguras** - Proteção contra ataques comuns
- **Usuário Admin Protegido** - Não pode ser excluído ou modificado
- **Bypass de Admin** - Usuário admin tem acesso total automático

### ✅ **Sistema de Validação Robusto**
- **Validação Server-side** - Verificação no servidor antes de salvar
- **Validação Client-side** - Feedback em tempo real no navegador
- **Tratamento de Erros** - Mensagens amigáveis para constraints únicos
- **Validação Centralizada** - Funções reutilizáveis em `utils/validation.py`
- **Campos Validados** - Email, nome, username, senha, telefone, datas

### 📊 **Dashboards Interativos**
- **Dashboard Principal** - Visão geral com gráficos de distribuição
- **Dashboard Vencimentos** - Análise temporal de documentos próximos ao vencimento
- **Dashboard Responsáveis** - Ranking e estatísticas por responsável
- **Dashboard Atividade** - Timeline de atividades e mudanças recentes
- **Dashboard de Usuários** - Estatísticas avançadas e métricas de login
- **Dashboard de Perfis** - Análise de roles e permissões

### 📧 **Sistema de Notificações**
- **Alertas Automáticos** - Envio semanal configurável
- **Alertas Manuais** - Envio sob demanda
- **Configurações SMTP** - Suporte a Gmail, Outlook, Office 365, Exchange
- **Teste de Email** - Validação de configurações em tempo real
- **SMTP4Dev** - Suporte para testes locais

### ⚙️ **Configurações Avançadas**
- **Agendamento Flexível** - Dias e horários personalizáveis
- **Toggle de Ativação** - Ativar/desativar agendamento
- **Configurações LDAP** - Integração com Active Directory
- **Teste de Conexão** - Validação de configurações LDAP
- **Personalização Simplificada** - Nome do sistema, equipe de TI e informações de contato

### 🎨 **Interface Moderna**
- **Bootstrap 5** - Design responsivo e moderno com gradientes
- **Modo Escuro** - Suporte completo com toggle
- **Chart.js** - Gráficos interativos e dinâmicos
- **Bootstrap Icons** - Ícones consistentes
- **Navegação Intuitiva** - Menus dropdown organizados
- **Design Limpo** - Interface simplificada sem configurações de cor desnecessárias
- **Formulários Validados** - Feedback visual em tempo real

## 🚀 Funcionalidades Detalhadas

### 📋 **Gestão de Registros**
- **CRUD Completo** - Criar, editar, excluir e visualizar registros
- **Categorização** - Certificados, senhas, licenças
- **Controle de Vencimento** - Datas de vencimento com alertas
- **Status de Regularização** - Controle de documentos regularizados
- **Filtros Avançados** - Busca por nome, tipo, responsável, status
- **Ordenação** - Múltiplos critérios de ordenação
- **Validação Completa** - Nome, origem, tipo, data futura, tempo de alerta

### 👥 **Gestão de Responsáveis**
- **Cadastro de Responsáveis** - Nome e email com validação
- **Atribuição Múltipla** - Um registro pode ter vários responsáveis
- **Estatísticas** - Contagem de itens por responsável
- **Ranking** - Top responsáveis com mais itens
- **Validação de Email** - Verificação de formato e unicidade

### 👤 **Gestão de Usuários (v2.2.0)**
- **Perfis Personalizáveis** - Criação de perfis com permissões específicas
- **Controle de Status** - Ativo, inativo, bloqueado
- **Reset de Senha** - Funcionalidade administrativa
- **Proteção do Admin** - Usuário admin não pode ser modificado
- **Histórico Completo** - Timeline de todas as ações do usuário
- **Dashboard Avançado** - Estatísticas, métricas e análise de atividade
- **Rastreamento de Login** - Último login, contagem de logins, IP address
- **Importação/Exportação** - Funcionalidades para gestão em lote
- **Campos Avançados** - Telefone, departamento, cargo, observações
- **Validação Robusta** - Username, email, nome, senha, telefone

### 📊 **Gestão de Perfis (v2.2.0)**
- **CRUD Completo** - Criar, editar, excluir e visualizar perfis
- **Dashboard Avançado** - Estatísticas e análise de roles
- **Clonagem de Perfis** - Sistema de templates e clonagem
- **Templates Pré-definidos** - Perfis base para cenários comuns
- **Assistente de Criação** - Wizard para criar perfis
- **Histórico Detalhado** - Timeline de mudanças com IP e user agent
- **Bulk Actions** - Ações em lote para múltiplos perfis
- **Importação/Exportação** - Funcionalidades para gestão em lote
- **Log de Alterações** - Histórico completo de criação, edição e exclusão

### 📊 **Relatórios e Analytics**
- **Dashboards em Tempo Real** - Dados atualizados dinamicamente
- **Gráficos Interativos** - Distribuição por status, tipo, responsável
- **Análise Temporal** - Vencimentos próximos e históricos
- **Métricas de Atividade** - Registros criados e modificados
- **Histórico Detalhado** - Timeline completa de ações com IP e user agent

## 🛠️ Requisitos Técnicos

### **Sistema Operacional**
- **Windows 10/11** ✅ (Scripts automáticos disponíveis)
- **Linux** ✅ (Detecção automática de distribuição):
  - **Ubuntu/Debian** (apt) ✅
  - **SUSE Linux Enterprise/openSUSE** (zypper) ✅  
  - **CentOS/RHEL/Fedora** (dnf) ✅
- **macOS** ✅ (Instalação manual)

### **Software**
- **Python 3.8+** (recomendado 3.11+)
- **PostgreSQL** (via Docker ou instalação local)
- **Git** (para controle de versão)

### **Dependências Python**
- **Flask 2.2+** - Framework web
- **Flask-Login** - Autenticação de usuários
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Principal** - Controle de permissões
- **Flask-Mail** - Envio de emails
- **APScheduler** - Agendamento de tarefas
- **ldap3** - Integração LDAP/Active Directory
- **psycopg2-binary** - Driver PostgreSQL
- **Chart.js** - Gráficos interativos (via CDN)
- **Bootstrap 5** - Framework CSS (via CDN)

## 📝 Mudanças Recentes

### **v2.5.0 - Configuração Segura do PostgreSQL**
- ✅ **Configuração Interativa Segura** - `configure_postgresql.py` sem credenciais hardcoded
- ✅ **Entrada Segura de Senhas** - Senhas não exibidas na tela durante configuração
- ✅ **Arquivo .env Protegido** - Configurações sensíveis em arquivo não versionado
- ✅ **SECRET_KEY Aleatória** - Geração automática de chaves seguras
- ✅ **Validação de Entrada** - Confirmação antes de aplicar configurações
- ✅ **Suporte Multi-plataforma** - Windows e Linux com detecção automática
- ✅ **Instalação Automática** - PostgreSQL instalado automaticamente no Linux
- ✅ **Scripts Atualizados** - `setup_vm.sh` e `setup_vm.bat` com configuração segura
- ✅ **Documentação de Segurança** - Guias completos para configuração segura
- ✅ **Guias Específicos por SO** - `INSTALACAO_WINDOWS.md`, `INSTALACAO_LINUX.md`, `INSTALACAO_MACOS.md`

### **v2.4.0 - Sistema de Validação e Correções**
- ✅ **Sistema de Validação Centralizado** - `utils/validation.py` com funções reutilizáveis
- ✅ **Validação Server-side** - Verificação no servidor antes de salvar dados
- ✅ **Validação Client-side** - Feedback em tempo real nos formulários
- ✅ **Tratamento de Erros** - Mensagens amigáveis para constraints únicos
- ✅ **Correção de Templates** - Campos corretos do `RoleHistory` e JavaScript
- ✅ **Sistema de Logs UTF-8** - Suporte completo a caracteres especiais
- ✅ **Rotas com Trailing Slashes** - Suporte a URLs com e sem `/`
- ✅ **Links Dinâmicos** - Conversão de links hardcoded para `url_for()`
- ✅ **Histórico de Perfis** - Log completo de criação, edição e exclusão
- ✅ **Correção de BuildError** - Endpoints corretos mapeados
- ✅ **Scripts Organizados** - Remoção de scripts temporários desnecessários
- ✅ **Regras do Cursor** - `.cursorrules` para orientação do AI

### **v2.3.0 - Limpeza e Scripts Unificados**
- ✅ **Scripts Unificados para Linux** - Detecção automática de distribuição (Ubuntu/Debian/SUSE/CentOS/Fedora)
- ✅ **Documentação Consolidada** - README único com todas as informações importantes
- ✅ **Projeto Limpo** - Removidos 16 arquivos redundantes e 2000+ linhas desnecessárias
- ✅ **Instalação Simplificada** - Scripts automáticos para Windows e Linux
- ✅ **Configuração de Firewall** - Suporte automático para múltiplos firewalls
- ✅ **Teste de Validação** - Script completo para validar instalação

### **v2.2.0 - Sistema de Histórico e Gerenciamento Avançado**
- ✅ **Histórico de Usuários** - Timeline completa de todas as ações
- ✅ **Dashboard de Usuários** - Estatísticas e métricas avançadas
- ✅ **Dashboard de Perfis** - Gerenciamento avançado de roles
- ✅ **Importação/Exportação** - Funcionalidades para usuários e perfis
- ✅ **Clonagem de Perfis** - Sistema de templates e clonagem
- ✅ **Rastreamento de Login** - Last login, login count, IP address
- ✅ **Cascade Delete** - Correção de integridade do banco
- ✅ **Scripts de Gerenciamento** - manage_db.py e quick_setup.py
- ✅ **Documentação Completa** - Guias detalhados
- ✅ **Suporte VM Inicial** - Scripts básicos para Windows e Linux

### **v2.1.0 - Interface Simplificada**
- ✅ **Removidas configurações de cor** - Interface mais limpa e consistente
- ✅ **Personalização simplificada** - Foco em informações essenciais
- ✅ **Design otimizado** - Gradientes Bootstrap padrão para melhor consistência
- ✅ **Código limpo** - Remoção de funcionalidades desnecessárias

## 🚀 Instalação e Configuração

### 📚 **Guias de Instalação por Sistema Operacional**

Para instruções detalhadas e específicas do seu sistema operacional, consulte os guias dedicados:

- **🖥️ Windows:** [Guia de Instalação Windows](INSTALACAO_WINDOWS.md)
- **🐧 Linux:** [Guia de Instalação Linux](INSTALACAO_LINUX.md)
- **🍎 macOS:** [Guia de Instalação macOS](INSTALACAO_MACOS.md)

### 🚀 **Instalação Rápida com Scripts Automáticos**

Para uma instalação mais fácil e rápida, use os scripts de automação:

#### **🖥️ Windows:**
```batch
# Configuração completa automática
setup_vm.bat

# Apenas configuração de rede/firewall
configure_network.bat
```

#### **🐧 Linux (Todas as Distribuições):**
```bash
# Configuração completa automática
chmod +x setup_vm.sh && ./setup_vm.sh

# Apenas configuração de rede/firewall
chmod +x configure_network.sh && ./configure_network.sh
```

**Distribuições Linux Suportadas:**
- ✅ **Ubuntu/Debian** (apt)
- ✅ **SUSE/openSUSE** (zypper)
- ✅ **CentOS/RHEL/Fedora** (dnf)
- ✅ **Detecção automática** da distribuição

#### **🍎 macOS:**
```bash
# Configuração completa automática
chmod +x setup_vm.sh && ./setup_vm.sh

# OU instalação manual com Homebrew
```

#### **📋 O que os Scripts Fazem:**
- **Verificam e instalam** Python 3, pip, venv, git
- **Criam ambiente virtual** automaticamente
- **Instalam dependências** do requirements.txt
- **Configuram banco de dados** com quick_setup.py
- **Configuram firewall** (Windows Firewall, UFW, firewalld, etc.)
- **Testam conectividade** nas portas 5000 (dev) e 80 (prod)
- **Iniciam a aplicação** automaticamente

### 🖥️ **Configuração Avançada em VM**
Para configuração detalhada em máquinas virtuais, consulte o [Guia de Configuração em VM](VM_SETUP_GUIDE.md) que inclui:
- Scripts de automação específicos
- Configuração de rede e firewall avançada
- Testes de validação completos
- Configuração como serviço do sistema
- Monitoramento e backup automático

### **📦 Instalação Manual (Resumo)**

#### **1. Clone o Repositório**
```bash
git clone https://github.com/felipesmk/sistema-certificados.git
cd sistema-certificados
```

#### **2. Ambiente Virtual**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

#### **4. Configuração Segura do PostgreSQL**
```bash
# Configuração interativa e segura (RECOMENDADO)
python configure_postgresql.py

# OU configuração manual
cp env.example .env
# Editar .env com suas credenciais PostgreSQL
```

#### **5. Configuração do Banco de Dados**
```bash
# Setup completo automático
python quick_setup.py setup

# OU configuração manual passo a passo
python manage_db.py migrate         # Criar/atualizar banco
python manage_db.py create-admin    # Criar usuário admin
```

#### **6. Configuração do Ambiente (Opcional)**
```bash
# Editar configurações adicionais (SMTP, LDAP, etc.)
# notepad .env  # Windows
# nano .env     # Linux
```

#### **6. Executar o Sistema**
```bash
# Desenvolvimento
python app.py

# Ou usando Flask
flask run

# Produção (Linux/macOS)
python run_production.py
```

#### **7. Acessar o Sistema**
- **Desenvolvimento:** http://localhost:5000
- **Produção:** http://localhost (porta 80)
- **Usuário padrão:** admin
- **Senha:** (definida durante o setup)

### **🔐 Segurança e Credenciais**

#### **Configuração Segura do PostgreSQL**
O sistema agora utiliza **configuração interativa e segura** para evitar credenciais hardcoded:

```bash
# Configuração interativa (RECOMENDADO)
python configure_postgresql.py
```

**Características de Segurança:**
- ✅ **Sem credenciais hardcoded** no código
- ✅ **Entrada segura de senhas** (não exibidas na tela)
- ✅ **Arquivo .env protegido** (não versionado)
- ✅ **SECRET_KEY aleatória** gerada automaticamente
- ✅ **Validação de entrada** do usuário
- ✅ **Confirmação** antes de aplicar configurações

#### **Arquivo .env Seguro**
O arquivo `.env` contém todas as configurações sensíveis:
```bash
# Exemplo de .env (NÃO versionado)
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/seu_banco
SECRET_KEY=sua_chave_secreta_aleatoria_aqui
MAIL_PASSWORD=sua_senha_de_email
```

**⚠️ Importante:**
- O arquivo `.env` **NÃO é versionado** no Git
- Mantenha suas credenciais **seguras e privadas**
- **Nunca** commite credenciais no repositório
- Use **senhas fortes** para produção

### **🔧 Configuração de Firewall Manual**

Se os scripts automáticos não funcionarem, configure o firewall manualmente:

#### **Windows:**
```batch
# Desenvolvimento (porta 5000)
netsh advfirewall firewall add rule name="Sistema Certificados Dev" dir=in action=allow protocol=TCP localport=5000

# Produção (porta 80)
netsh advfirewall firewall add rule name="Sistema Certificados Prod" dir=in action=allow protocol=TCP localport=80
```

#### **Linux:**
```bash
# Desenvolvimento (porta 5000)
sudo ufw allow 5000

# Produção (porta 80)
sudo ufw allow 80

# CentOS/RHEL/Fedora (firewalld)
sudo firewall-cmd --permanent --add-port=5000/tcp  # Desenvolvimento
sudo firewall-cmd --permanent --add-port=80/tcp    # Produção
sudo firewall-cmd --reload

# SUSE (firewalld ou SuSEfirewall2)
sudo firewall-cmd --permanent --add-port=5000/tcp  # Desenvolvimento
sudo firewall-cmd --permanent --add-port=80/tcp    # Produção
sudo firewall-cmd --reload
# OU
sudo SuSEfirewall2 open EXT TCP 5000  # Desenvolvimento
sudo SuSEfirewall2 open EXT TCP 80    # Produção
```

## 🔐 Estrutura de Permissões e Perfis

### **Permissões do Sistema**
| Permissão | Descrição | Acesso |
|-----------|-----------|---------|
| `manage_access` | Gerenciar usuários e perfis | Administradores |
| `manage_registros` | Gerenciar registros | Operadores |
| `manage_responsaveis` | Gerenciar responsáveis | Operadores |
| `manage_config` | Gerenciar configurações | Administradores |
| `send_alerts` | Enviar alertas por email | Operadores |
| `view_data` | Visualizar dados | Visualizadores |

### **Perfis Padrão**
| Perfil | Permissões | Descrição |
|--------|------------|-----------|
| **admin** | Todas as permissões | Administrador completo do sistema |
| **operador** | registros, responsáveis, alertas | Pode gerenciar dados e enviar alertas |
| **visualizador** | Apenas visualização | Acesso somente leitura |

### **Características Especiais**
- **Usuário Admin Protegido** - Não pode ser excluído ou modificado
- **Bypass de Admin** - Usuário admin tem acesso total automático
- **Perfis Customizáveis** - Novos perfis podem ser criados
- **Permissões Granulares** - Controle fino de acesso
- **Menus Dinâmicos** - Interface adapta-se às permissões

## 🛠️ Comandos Úteis

### **Desenvolvimento**
```bash
# Configuração segura do PostgreSQL (PRIMEIRO PASSO)
python configure_postgresql.py      # Configuração interativa e segura

# Setup completo automático (RECOMENDADO)
python quick_setup.py setup

# Gerenciamento manual do banco
python manage_db.py status          # Verificar status do banco
python manage_db.py migrate         # Executar migrações
python manage_db.py reset           # Resetar banco (CUIDADO!)
python manage_db.py create-admin    # Criar usuário admin
python manage_db.py create-user     # Criar usuário adicional
python manage_db.py backup          # Backup do banco
python manage_db.py restore         # Restaurar backup

# Testes e validação
python quick_setup.py test-users    # Testar funcionalidades de usuários
python quick_setup.py test-suse     # Testar compatibilidade SUSE
python test_vm_installation.py      # Teste completo da instalação VM
python test_validation.py           # Testar sistema de validação

# Executar em modo desenvolvimento
python app.py
```

### **Scripts de VM e Instalação**
```bash
# Windows - Setup completo
setup_vm.bat                        # Instala tudo e inicia aplicação

# Windows - Apenas rede
configure_network.bat               # Configura firewall e testa conectividade

# Linux - Setup completo (detecta distro automaticamente)
chmod +x setup_vm.sh && ./setup_vm.sh

# Linux - Apenas rede  
chmod +x configure_network.sh && ./configure_network.sh

# Teste de validação completo
python test_vm_installation.py     # Valida instalação, dependências, banco, rede
```

### **Verificação de Status**
```bash
# Verificar se tudo está funcionando
python manage_db.py status          # Status do banco de dados
python quick_setup.py status        # Status geral do sistema
python test_vm_installation.py      # Teste completo de validação

# Verificar logs
tail -f logs/app.log                # Logs da aplicação
dir logs                            # Windows: ver arquivos de log
ls -la logs/                        # Linux: ver arquivos de log
```

### **Solução de Problemas**
```bash
# Problema: Erro de migração do banco
python manage_db.py reset --force    # Resetar banco (CUIDADO! Apaga dados)
python manage_db.py migrate          # Recriar estrutura
python manage_db.py create-admin     # Recriar admin

# Problema: Porta em uso
netstat -tlnp | grep 5000           # Linux: verificar porta 5000 (desenvolvimento)
netstat -tlnp | grep 80             # Linux: verificar porta 80 (produção)
netstat -an | findstr 5000          # Windows: verificar porta 5000 (desenvolvimento)
netstat -an | findstr 80            # Windows: verificar porta 80 (produção)

# Problema: Dependências não instaladas
pip install --upgrade pip           # Atualizar pip
pip install -r requirements.txt     # Reinstalar dependências

# Problema: Ambiente virtual corrompido
rm -rf venv                          # Linux: remover venv
rmdir /s venv                       # Windows: remover venv
python -m venv venv                 # Recriar ambiente virtual

# Problema: Firewall bloqueando
python test_vm_installation.py     # Testar conectividade
# Seguir instruções de firewall acima
```

### **Produção**
```bash
# Instalar dependências de produção primeiro
python quick_setup.py install-prod

# Executar servidor de produção
python run_production.py

# Ou usar comandos diretos:
# Linux/macOS (Gunicorn)
gunicorn -c gunicorn.conf.py app:app

# Windows (Waitress)
waitress-serve --host=0.0.0.0 --port=80 app:app
```

### **Solução de Problemas - Produção**
```bash
# Problema: "No such file or directory: 'gunicorn'"
python quick_setup.py install-prod   # Instalar dependências automaticamente

# Ou instalar manualmente:
pip install gunicorn                 # Linux/macOS
pip install waitress                 # Windows

# Problema: Porta 80 em uso
python run_production.py             # Usa porta 80 por padrão
# Ou especificar porta diferente:
gunicorn --bind 0.0.0.0:8080 app:app  # Porta alternativa se 80 estiver ocupada
```

### **Solução de Problemas - SUSE Linux**
```bash
# Problema: Pacotes Python não encontrados no SUSE
python quick_setup.py test-suse     # Testar compatibilidade específica

# Problema: Flask não instala no SUSE
pip install --upgrade pip           # Atualizar pip primeiro
pip install Flask>=2.2.0            # Instalar Flask individualmente

# Problema: Dependências do sistema não encontradas
sudo zypper refresh                 # Atualizar repositórios
sudo zypper install python3 python3-pip3 python3-virtualenv git-core

# Verificar instalação
python -c "import flask; print(flask.__version__)"
```



## 💡 Dicas para Desenvolvimento

### **Fluxo de Trabalho**
1. **Sempre execute** `quick_setup.py setup` para configuração completa
2. **O usuário admin** sempre terá o perfil admin com bypass automático
3. **Menus e rotas** são exibidos conforme permissões
4. **Para novas permissões** - edite `manage_db.py` e associe aos perfis
5. **Use validação centralizada** - `utils/validation.py` para novos campos

### **Boas Práticas**
- **Ambiente virtual** sempre ativo durante desenvolvimento
- **Logs** são salvos em `logs/app.log` com encoding UTF-8
- **Configurações** em arquivo `.env` (não versionado)
- **Testes** de email com SMTP4Dev para desenvolvimento
- **Validação dupla** - Sempre implementar server-side + client-side
- **Tratamento de erros** - Usar mensagens amigáveis para constraints

## 📁 Estrutura do Projeto

```
sistema-certificados/
├── app.py                 # Aplicação principal e rotas
├── models.py              # Modelos do banco de dados
├── manage_db.py           # Gerenciamento unificado do banco
├── quick_setup.py         # Setup rápido e testes
├── run_production.py      # Servidor de produção
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── .gitignore            # Arquivos ignorados pelo Git
├── .cursorrules          # Regras do Cursor AI
├── README.md             # Documentação principal
├── VM_SETUP_GUIDE.md     # Guia de configuração em VM
├── CHANGELOG.md          # Histórico de mudanças
├── setup_vm.bat          # Script de automação Windows
├── configure_network.bat # Configuração de rede Windows
├── setup_vm.sh           # Script unificado Linux (Ubuntu/Debian/SUSE/CentOS/Fedora)
├── configure_network.sh  # Rede unificada Linux
├── test_vm_installation.py # Teste de validação da VM
├── test_validation.py    # Testes do sistema de validação
├── configure_postgresql.py # Configuração segura do PostgreSQL
├── INSTALACAO_WINDOWS.md # Guia detalhado para Windows
├── INSTALACAO_LINUX.md   # Guia detalhado para Linux
├── INSTALACAO_MACOS.md   # Guia detalhado para macOS
├── utils/                # Utilitários
│   ├── __init__.py       # Package init
│   ├── validation.py     # Sistema de validação centralizado
│   ├── cache.py          # Sistema de cache
│   └── pagination.py     # Sistema de paginação
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── dashboard*.html   # Dashboards
│   ├── registros/        # CRUD de registros (com validação)
│   ├── responsaveis/     # CRUD de responsáveis (com validação)
│   ├── usuarios/         # CRUD de usuários (com validação)
│   ├── perfis/           # CRUD de perfis (com histórico)
│   └── configuracao/     # Configurações do sistema
├── routes/               # Blueprints de rotas (auth.py)
├── logs/                 # Logs da aplicação (UTF-8)
└── instance/             # Banco SQLite (legado, não versionado)
```

## 🚀 Deploy e Produção

### **Configuração Inicial**

1. **Configure as variáveis de ambiente**:
   ```bash
   cp env.example .env
   # Edite o arquivo .env com suas configurações
   ```

2. **Instale as dependências de produção**:
   ```bash
   pip install -r requirements.txt
   ```

### Executando em Produção

#### Opção 1: Script Automático (Recomendado)
```bash
python run_production.py
```

#### Opção 2: Gunicorn Manual
```bash
gunicorn --config gunicorn.conf.py app:app
```

#### Opção 3: Comando Simples
```bash
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

### Configurações de Produção

#### Variáveis de Ambiente Importantes
- `FLASK_ENV=production`: Define modo produção
- `SECRET_KEY`: Chave secreta forte e fixa
- `DATABASE_URL`: URL do banco de dados PostgreSQL
- `MAIL_*`: Configurações de email
- `AUTH_MODE`: Modo de autenticação ('banco' ou 'ldap')
- `PERMANENT_SESSION_LIFETIME`: Tempo de sessão em segundos

#### Logs
- **Aplicação**: `logs/app.log` (com rotação automática e UTF-8)
- **Gunicorn**: `logs/gunicorn_access.log` e `logs/gunicorn_error.log`
- **Nível**: INFO (configurável via `LOG_LEVEL`)

#### Segurança
- ✅ Logs em arquivo com rotação e UTF-8
- ✅ Configuração via variáveis de ambiente
- ✅ Sessões com tempo de expiração
- ✅ Suporte a HTTPS (configure no Gunicorn)
- ✅ Validação robusta de dados
- ✅ Tratamento de erros de constraint
- ⚠️ Configure firewall e acesso restrito
- ⚠️ Use HTTPS em produção
- ⚠️ Monitore logs regularmente

#### Performance
- **Workers**: Configurado automaticamente (CPU cores × 2 + 1)
- **Timeout**: 30 segundos
- **Max Requests**: 1000 por worker (com jitter)
- **Keepalive**: 2 segundos

### Monitoramento

#### Verificar Status
```bash
# Verificar se o processo está rodando
ps aux | grep gunicorn

# Verificar logs
tail -f logs/app.log
tail -f logs/gunicorn_access.log
```

#### Reiniciar Serviço
```bash
# Parar processo atual
pkill gunicorn

# Iniciar novamente
python run_production.py
```

## 🔧 Gerenciamento de Banco de Dados

### **Comandos Principais**
```bash
# Verificar status do banco
python manage_db.py status

# Executar migrações
python manage_db.py migrate

# Resetar banco (CUIDADO!)
python manage_db.py reset

# Criar usuário admin
python manage_db.py create-admin

# Criar usuário adicional
python manage_db.py create-user

# Backup do banco
python manage_db.py backup

# Restaurar backup
python manage_db.py restore
```

### **Migrações Automáticas**
O sistema inclui migrações automáticas para:
- Campos LDAP (last_ldap_sync, is_ldap_role)
- Campos avançados de usuário (created_at, last_login, etc.)
- Campos avançados de perfil (ativo, cor, icone, etc.)
- Tabelas de histórico (user_history, role_history)
- Sistema de validação e constraints únicos

## 🔐 Integração LDAP/Active Directory

### **Configuração**
1. Configure as variáveis LDAP no arquivo `.env`
2. Execute `python manage_db.py migrate` para adicionar campos LDAP
3. Teste a conexão em Configurações > LDAP

### **Funcionalidades**
- **Autenticação automática** com credenciais do AD
- **Sincronização de dados** (nome, email, departamento)
- **Mapeamento de grupos** para perfis
- **Cache de conexão** para melhor performance
- **Timeout configurável** para conexões

## 🤝 Contribuição

### **Como Contribuir**
1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### **Padrões de Código**
- **Python**: PEP 8
- **HTML**: Indentação consistente
- **CSS**: Organização por seções
- **JavaScript**: ES6+ quando possível
- **Validação**: Sempre implementar server-side + client-side
- **Logs**: Usar encoding UTF-8

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **Flask** - Framework web Python
- **Bootstrap** - Framework CSS
- **Chart.js** - Biblioteca de gráficos
- **Bootstrap Icons** - Ícones
- **SMTP4Dev** - Servidor SMTP para testes
- **PostgreSQL** - Banco de dados robusto

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

Para dúvidas ou sugestões, abra uma issue ou entre em contato com o mantenedor. 