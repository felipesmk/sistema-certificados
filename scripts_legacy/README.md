# 📁 Scripts Legacy

Esta pasta contém os scripts antigos do sistema, que foram **substituídos** pelo script unificado `manage_db.py`.

## ⚠️ **Scripts Descontinuados:**

- `init_db.py` → **Use**: `python manage_db.py init`
- `create_admin.py` → **Use**: `python manage_db.py create-admin`
- `create_user.py` → **Use**: `python manage_db.py create-user`
- `migrate_ldap_fields.py` → **Use**: `python manage_db.py migrate`
- `migrate_advanced_roles.py` → **Use**: `python manage_db.py migrate`

## 🚀 **Script Unificado:**

Todo o gerenciamento de banco de dados agora é feito através do script principal:

```bash
python manage_db.py [comando]
```

### 📋 **Comandos Disponíveis:**

- `init` - Inicializar banco novo
- `reset` - Reset completo do banco
- `create-admin` - Criar usuário admin
- `create-user` - Criar usuário comum
- `migrate` - Executar migrações
- `backup` - Criar backup
- `restore` - Restaurar backup
- `status` - Ver status do banco

---

*Estes scripts estão mantidos apenas para referência histórica e podem ser removidos no futuro.*