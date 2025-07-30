# 📝 Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [2.1.0] - 2025-01-25

### ✅ Adicionado
- Seção "Mudanças Recentes" no README.md
- Arquivo CHANGELOG.md para documentação de versões
- Documentação sobre interface simplificada

### 🗑️ Removido
- Configurações de cor primária e secundária do sistema
- Campos de seleção de cor na interface de configurações
- Colunas `cor_primaria` e `cor_secundaria` da tabela `Configuracao`
- Referências às cores no código backend
- Funcionalidades de personalização de cores desnecessárias

### 🔧 Alterado
- Interface de configurações simplificada
- Foco em configurações essenciais: nome do sistema, equipe de TI, informações de contato
- Design mais limpo e consistente usando gradientes Bootstrap padrão
- Documentação atualizada para refletir as mudanças

### 🐛 Corrigido
- Código mais limpo sem funcionalidades desnecessárias
- Interface mais intuitiva e focada

## [2.0.0] - 2025-01-XX

### ✅ Adicionado
- Sistema completo de gestão de certificados
- Autenticação LDAP/Active Directory
- Dashboards interativos
- Sistema de notificações por email
- Controle de acesso baseado em perfis (RBAC)
- Configurações avançadas do sistema
- Interface moderna com Bootstrap 5

### 🔧 Funcionalidades Principais
- Gestão de registros (certificados, senhas, licenças)
- Gestão de responsáveis
- Gestão de usuários e perfis
- Alertas automáticos de vencimento
- Configurações de email e LDAP
- Dashboards com gráficos interativos

---

## Como Contribuir

Para adicionar uma nova entrada ao changelog:

1. Adicione uma nova seção `[X.Y.Z]` no topo do arquivo
2. Use os tipos: `✅ Adicionado`, `🔧 Alterado`, `🗑️ Removido`, `🐛 Corrigido`
3. Inclua a data no formato YYYY-MM-DD
4. Descreva as mudanças de forma clara e concisa 