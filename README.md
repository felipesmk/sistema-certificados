# 🏢 Sistema de Gestão de Certificados e Documentos Controlados

## 📋 Visão Geral

Sistema web completo para gestão de certificados, senhas, licenças e documentos controlados com controle de acesso baseado em perfis (RBAC). Desenvolvido em Flask com interface moderna, dashboards interativos e funcionalidades avançadas de autenticação e notificação.

## ✨ Funcionalidades Principais

### 🔐 **Segurança e Autenticação**
- **RBAC Completo** - Controle de acesso baseado em perfis e permissões
- **Autenticação Dupla** - Banco de dados ou LDAP/Active Directory
- **Sessões Seguras** - Proteção contra ataques comuns
- **Usuário Admin Protegido** - Não pode ser excluído ou modificado

### 📊 **Dashboards Interativos**
- **Dashboard Principal** - Visão geral com gráficos de distribuição
- **Dashboard Vencimentos** - Análise temporal de documentos próximos ao vencimento
- **Dashboard Responsáveis** - Ranking e estatísticas por responsável
- **Dashboard Atividade** - Timeline de atividades e mudanças recentes

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

## 🚀 Funcionalidades Detalhadas

### 📋 **Gestão de Registros**
- **CRUD Completo** - Criar, editar, excluir e visualizar registros
- **Categorização** - Certificados, senhas, licenças
- **Controle de Vencimento** - Datas de vencimento com alertas
- **Status de Regularização** - Controle de documentos regularizados
- **Filtros Avançados** - Busca por nome, tipo, responsável, status
- **Ordenação** - Múltiplos critérios de ordenação

### 👥 **Gestão de Responsáveis**
- **Cadastro de Responsáveis** - Nome e email
- **Atribuição Múltipla** - Um registro pode ter vários responsáveis
- **Estatísticas** - Contagem de itens por responsável
- **Ranking** - Top responsáveis com mais itens

### 👤 **Gestão de Usuários**
- **Perfis Personalizáveis** - Criação de perfis com permissões específicas
- **Controle de Status** - Ativo, inativo, bloqueado
- **Reset de Senha** - Funcionalidade administrativa
- **Proteção do Admin** - Usuário admin não pode ser modificado
- **Histórico Completo** - Timeline de todas as ações do usuário
- **Dashboard Avançado** - Estatísticas, métricas e análise de atividade
- **Rastreamento de Login** - Último login, contagem de logins, IP address
- **Importação/Exportação** - Funcionalidades para gestão em lote
- **Campos Avançados** - Telefone, departamento, cargo, observações

### 📊 **Relatórios e Analytics**
- **Dashboards em Tempo Real** - Dados atualizados dinamicamente
- **Gráficos Interativos** - Distribuição por status, tipo, responsável
- **Análise Temporal** - Vencimentos próximos e históricos
- **Métricas de Atividade** - Registros criados e modificados
- **Dashboard de Usuários** - Estatísticas avançadas e métricas de login
- **Dashboard de Perfis** - Análise de roles e permissões
- **Histórico Detalhado** - Timeline completa de ações com IP e user agent

## 🛠️ Requisitos Técnicos

### **Sistema Operacional**
- **Windows 10/11** ✅
- **Linux** ✅
- **macOS** ✅

### **Software**
- **Python 3.8+** (recomendado 3.11+)
- **SQLite 3** (incluído no Python)
- **Git** (para controle de versão)

### **Dependências Python**
- **Flask 2.2+** - Framework web
- **Flask-Login** - Autenticação de usuários
- **Flask-SQLAlchemy** - ORM para banco de dados
- **Flask-Principal** - Controle de permissões
- **Flask-Mail** - Envio de emails
- **APScheduler** - Agendamento de tarefas
- **ldap3** - Integração LDAP/Active Directory
- **Chart.js** - Gráficos interativos (via CDN)
- **Bootstrap 5** - Framework CSS (via CDN)

## 📝 Mudanças Recentes

### **v2.2.0 - Sistema de Histórico e Gerenciamento Avançado**
- ✅ **Histórico de Usuários** - Timeline completa de todas as ações
- ✅ **Dashboard de Usuários** - Estatísticas e métricas avançadas
- ✅ **Dashboard de Perfis** - Gerenciamento avançado de roles
- ✅ **Importação/Exportação** - Funcionalidades para usuários e perfis
- ✅ **Clonagem de Perfis** - Sistema de templates e clonagem
- ✅ **Rastreamento de Login** - Last login, login count, IP address
- ✅ **Cascade Delete** - Correção de integridade do banco
- ✅ **Scripts Unificados** - manage_db.py e quick_setup.py
- ✅ **Documentação Completa** - 5 guias detalhados

### **v2.1.0 - Interface Simplificada**
- ✅ **Removidas configurações de cor** - Interface mais limpa e consistente
- ✅ **Personalização simplificada** - Foco em informações essenciais
- ✅ **Design otimizado** - Gradientes Bootstrap padrão para melhor consistência
- ✅ **Código limpo** - Remoção de funcionalidades desnecessárias

## 🚀 Instalação e Configuração

### **1. Clone o Repositório**
```bash
git clone <url-do-repositorio>
cd Projetoteste
```

### **2. Ambiente Virtual**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### **3. Instalar Dependências**
```bash
pip install -r requirements.txt
```

### **4. Configuração Inicial**
```bash
# Setup completo automático (RECOMENDADO)
python quick_setup.py setup

# Ou configuração manual:
# Inicializar banco de dados e permissões
python manage_db.py migrate

# Criar usuário administrador
python manage_db.py create-admin
```

### **5. Executar o Sistema**
```bash
# Desenvolvimento
python app.py

# Ou usando Flask
flask run
```

### **6. Acessar o Sistema**
- **URL:** http://localhost:5000
- **Usuário:** admin
- **Senha:** (definida no create_admin.py)

## 🔐 Estrutura de Permissões e Perfis

### **Permissões do Sistema**
| Permissão | Descrição | Acesso |
|-----------|-----------|---------|
| `manage_access` | Gerenciar usuários e perfis | Administradores |
| `manage_registros` | Gerenciar registros | Operadores |
| `manage_responsaveis` | Gerenciar responsáveis | Operadores |
| `manage_config` | Gerenciar configurações | Administradores |
| `send_alerts` | Enviar alertas por email | Operadores |

### **Perfis Padrão**
| Perfil | Permissões | Descrição |
|--------|------------|-----------|
| **admin** | Todas as permissões | Administrador completo do sistema |
| **operador** | registros, responsáveis, alertas | Pode gerenciar dados e enviar alertas |
| **visualizador** | Apenas visualização | Acesso somente leitura |

### **Características Especiais**
- **Usuário Admin Protegido** - Não pode ser excluído ou modificado
- **Perfis Customizáveis** - Novos perfis podem ser criados
- **Permissões Granulares** - Controle fino de acesso
- **Menus Dinâmicos** - Interface adapta-se às permissões

## 🛠️ Comandos Úteis

### **Desenvolvimento**
```bash
# Setup completo automático (RECOMENDADO)
python quick_setup.py setup

# Gerenciamento manual do banco
python manage_db.py status          # Verificar status do banco
python manage_db.py migrate         # Executar migrações
python manage_db.py reset           # Resetar banco (CUIDADO!)
python manage_db.py create-admin    # Criar usuário admin
python manage_db.py create-user     # Criar usuário adicional

# Testes e validação
python quick_setup.py test-users    # Testar funcionalidades de usuários

# Executar em modo desenvolvimento
python app.py
```

### **Produção**
```bash
# Executar servidor de produção
python run_production.py

# Usando Gunicorn (Linux/macOS)
gunicorn -c gunicorn.conf.py app:app

# Usando Waitress (Windows)
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

## 💡 Dicas para Desenvolvimento

### **Fluxo de Trabalho**
1. **Sempre execute** `init_db.py` antes de `create_admin.py`
2. **O usuário admin** sempre terá o perfil admin
3. **Menus e rotas** são exibidos conforme permissões
4. **Para novas permissões** - edite `init_db.py` e associe aos perfis

### **Boas Práticas**
- **Ambiente virtual** sempre ativo durante desenvolvimento
- **Logs** são salvos em `logs/app.log`
- **Configurações** em arquivo `.env` (não versionado)
- **Testes** de email com SMTP4Dev para desenvolvimento

## 📁 Estrutura do Projeto

```
Projetoteste/
├── app.py                 # Aplicação principal e rotas
├── models.py              # Modelos do banco de dados
├── manage_db.py           # Gerenciamento unificado do banco
├── quick_setup.py         # Setup rápido e testes
├── run_production.py      # Servidor de produção
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Documentação
├── DATABASE_MANAGEMENT.md # Guia de gerenciamento do banco
├── USER_MANAGEMENT_IMPROVEMENTS.md # Melhorias de usuários
├── ROLES_MANAGEMENT_GUIDE.md # Guia de perfis
├── LDAP_IMPROVEMENTS.md  # Melhorias LDAP
├── SCRIPTS_IMPROVEMENTS.md # Melhorias dos scripts
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── dashboard*.html   # Dashboards
│   ├── registros/        # CRUD de registros
│   ├── responsaveis/     # CRUD de responsáveis
│   ├── usuarios/         # CRUD de usuários (com histórico)
│   ├── perfis/           # CRUD de perfis (com dashboard)
│   └── configuracao/     # Configurações do sistema
├── scripts_legacy/       # Scripts antigos (preservados)
├── static/               # Arquivos estáticos
├── logs/                 # Logs da aplicação
└── instance/             # Banco de dados (não versionado)
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
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Configurações de Produção

#### Variáveis de Ambiente Importantes
- `FLASK_ENV=production`: Define modo produção
- `SECRET_KEY`: Chave secreta forte e fixa
- `DATABASE_URL`: URL do banco de dados
- `MAIL_*`: Configurações de email
- `AUTH_MODE`: Modo de autenticação ('banco' ou 'ldap')
- `PERMANENT_SESSION_LIFETIME`: Tempo de sessão em segundos

#### Logs
- **Aplicação**: `logs/app.log` (com rotação automática)
- **Gunicorn**: `logs/gunicorn_access.log` e `logs/gunicorn_error.log`
- **Nível**: INFO (configurável via `LOG_LEVEL`)

#### Segurança
- ✅ Logs em arquivo com rotação
- ✅ Configuração via variáveis de ambiente
- ✅ Sessões com tempo de expiração
- ✅ Suporte a HTTPS (configure no Gunicorn)
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

---

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

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

- **Flask** - Framework web Python
- **Bootstrap** - Framework CSS
- **Chart.js** - Biblioteca de gráficos
- **Bootstrap Icons** - Ícones
- **SMTP4Dev** - Servidor SMTP para testes

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela!**

Para dúvidas ou sugestões, abra uma issue ou entre em contato com o mantenedor. 