# 🗄️ **Sistema de Gerenciamento de Banco de Dados**

## 📋 **Visão Geral**

O sistema agora possui um **gerenciamento unificado** de banco de dados através de scripts modernos e organizados.

---

## 🚀 **Scripts Principais**

### 1. **`manage_db.py`** - Gerenciador Principal
**Script unificado** para todas as operações de banco:

```bash
python manage_db.py [comando] [opções]
```

#### 📋 **Comandos Disponíveis:**

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `init` | Inicializar banco novo | `python manage_db.py init` |
| `reset` | Reset completo do banco | `python manage_db.py reset` |
| `create-admin` | Criar usuário admin | `python manage_db.py create-admin` |
| `create-user` | Criar usuário comum | `python manage_db.py create-user user1 "Nome" email@test.com senha123` |
| `migrate` | Executar migrações | `python manage_db.py migrate` |
| `backup` | Criar backup | `python manage_db.py backup` |
| `restore` | Restaurar backup | `python manage_db.py restore backup.db` |
| `status` | Ver status do banco | `python manage_db.py status` |

### 2. **`quick_setup.py`** - Setup Rápido
**Script interativo** para configurações comuns:

```bash
python quick_setup.py
```

#### 🎯 **Opções do Menu:**
- **🚀 Setup Completo** - Reset + admin + migrações + backup
- **⚡ Início Rápido** - Apenas migrações necessárias
- **👥 Usuários Demo** - Cria usuários de teste
- **💾 Backup Sistema** - Backup rápido
- **📊 Status** - Verificação do sistema

#### 📝 **Uso por Linha de Comando:**
```bash
python quick_setup.py setup    # Setup completo
python quick_setup.py start    # Início rápido
python quick_setup.py demo     # Usuários demo
python quick_setup.py backup   # Backup
python quick_setup.py status   # Status
```

---

## 🎯 **Cenários de Uso**

### 🆕 **Primeiro Setup (Sistema Novo):**
```bash
# Opção 1: Automático
python quick_setup.py setup

# Opção 2: Manual
python manage_db.py reset
python manage_db.py create-admin
python manage_db.py migrate
python manage_db.py backup
```

### ⚡ **Início Rápido (Sistema Existente):**
```bash
# Opção 1: Automático
python quick_setup.py start

# Opção 2: Manual
python manage_db.py migrate
python manage_db.py status
```

### 👥 **Desenvolvimento com Dados de Teste:**
```bash
python quick_setup.py demo
# Cria: operador1/123456, visual1/123456, gestor1/123456
```

### 🔧 **Manutenção Regular:**
```bash
python manage_db.py backup     # Backup antes de mudanças
python manage_db.py migrate    # Aplicar atualizações
python manage_db.py status     # Verificar saúde
```

---

## 📊 **Funcionalidades Avançadas**

### 💾 **Sistema de Backup:**
- **Backup automático** antes de operações críticas
- **Rotação de backups** (mantém 10 mais recentes)
- **Restore simples** com validação
- **Pasta organizada** (`backups/`)

### 🔄 **Migrações Inteligentes:**
- **Detecção automática** de campos faltantes
- **Aplicação incremental** de mudanças
- **Rollback seguro** em caso de erro
- **Índices otimizados** para performance

### 🎨 **Interface Visual:**
- **Cores no terminal** para melhor visibilidade
- **Ícones informativos** (✅ ❌ ⚠️ ℹ️)
- **Progress feedback** em tempo real
- **Mensagens claras** e detalhadas

### 🛡️ **Validações de Segurança:**
- **Confirmação** para operações destrutivas
- **Verificação** de integridade
- **Backup automático** antes de reset
- **Validação** de dados críticos

---

## 📁 **Estrutura de Arquivos**

```
📁 Projetoteste/
├── 🗄️ manage_db.py          # Script principal
├── ⚡ quick_setup.py         # Setup rápido
├── 📁 backups/               # Backups automáticos
├── 📁 scripts_legacy/        # Scripts antigos (descontinuados)
│   ├── init_db.py
│   ├── create_admin.py
│   ├── create_user.py
│   ├── migrate_*.py
│   └── README.md
└── 📁 instance/
    └── certificados.db       # Banco SQLite
```

---

## 🔧 **Funcionalidades Técnicas**

### 🏗️ **Arquitetura Modular:**
```python
class DatabaseManager:
    ├── init_database()       # Inicialização completa
    ├── create_user()         # Gestão de usuários
    ├── backup_database()     # Sistema de backup
    ├── migrate_database()    # Migrações automáticas
    └── status()              # Diagnósticos
```

### 📊 **Dados Criados Automaticamente:**

#### 🔐 **Permissões Padrão:**
- `manage_access` (sistema/crítica)
- `manage_registros` (dados/alta)
- `manage_responsaveis` (dados/média)
- `manage_config` (sistema/crítica)
- `send_alerts` (comunicação/média)

#### 🎭 **Roles Padrão:**
- **Admin** (🔴 todas permissões, prioridade 10)
- **Operador** (🔵 operações básicas, prioridade 5)
- **Visualizador** (⚫ apenas leitura, prioridade 1)

#### 📝 **Templates Padrão:**
- **Administrador Departamental** (gestão)
- **Operador Sistema** (operacional)
- **Visualizador** (consulta)
- **Auditor** (auditoria)

---

## 🚨 **Troubleshooting**

### ❌ **Problemas Comuns:**

#### 1. **"Banco não encontrado"**
```bash
python manage_db.py init
```

#### 2. **"Admin não existe"**
```bash
python manage_db.py create-admin
```

#### 3. **"Campos faltando"**
```bash
python manage_db.py migrate
```

#### 4. **"Banco corrompido"**
```bash
python manage_db.py restore ultimo_backup.db
```

### 🔧 **Comandos de Diagnóstico:**
```bash
python manage_db.py status          # Status completo
python quick_setup.py status        # Status rápido
ls -la instance/                     # Verificar arquivos
ls -la backups/                      # Ver backups disponíveis
```

---

## 📈 **Benefícios do Novo Sistema**

### ✅ **Para Desenvolvedores:**
- **Script único** em vez de 5 separados
- **Comandos padronizados** e consistentes
- **Backup automático** antes de mudanças
- **Validações robustas** contra erros

### ✅ **Para Administradores:**
- **Setup automatizado** para novos ambientes
- **Usuários demo** para testes rápidos
- **Backups organizados** com rotação
- **Status detalhado** do sistema

### ✅ **Para o Sistema:**
- **Migrações incrementais** sem perda de dados
- **Rollback seguro** em caso de problemas
- **Performance otimizada** com índices
- **Manutenção simplificada**

---

## 🎯 **Migração de Scripts Antigos**

### 📋 **Equivalências:**

| Script Antigo | Novo Comando |
|---------------|--------------|
| `python init_db.py` | `python manage_db.py init` |
| `python create_admin.py` | `python manage_db.py create-admin` |
| `python create_user.py` | `python manage_db.py create-user` |
| `python migrate_ldap_fields.py` | `python manage_db.py migrate` |
| `python migrate_advanced_roles.py` | `python manage_db.py migrate` |

### 🗑️ **Scripts Descontinuados:**
Os scripts antigos foram movidos para `scripts_legacy/` e podem ser removidos após validação completa.

---

*Sistema de Gerenciamento Unificado v2.4.0 - Todas as operações de banco simplificadas!* 🚀