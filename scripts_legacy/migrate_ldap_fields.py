#!/usr/bin/env python3
"""
Script de migração para adicionar campos LDAP aos modelos existentes.
Execute após ativar o ambiente virtual.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role
from sqlalchemy import text

def migrate_ldap_fields():
    """Adiciona novos campos LDAP ao banco de dados."""
    print("🔄 Iniciando migração dos campos LDAP...")
    
    with app.app_context():
        try:
            # Verificar se as colunas já existem
            inspector = db.inspect(db.engine)
            
            # Verificar campos na tabela User
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            if 'last_ldap_sync' not in user_columns:
                print("➕ Adicionando campo 'last_ldap_sync' à tabela User...")
                db.engine.execute(text("ALTER TABLE user ADD COLUMN last_ldap_sync DATETIME"))
            else:
                print("✅ Campo 'last_ldap_sync' já existe na tabela User")
            
            # Verificar campos na tabela Role
            role_columns = [col['name'] for col in inspector.get_columns('role')]
            if 'is_ldap_role' not in role_columns:
                print("➕ Adicionando campo 'is_ldap_role' à tabela Role...")
                db.engine.execute(text("ALTER TABLE role ADD COLUMN is_ldap_role BOOLEAN DEFAULT 0"))
                # Criar índice
                db.engine.execute(text("CREATE INDEX IF NOT EXISTS ix_role_is_ldap_role ON role (is_ldap_role)"))
            else:
                print("✅ Campo 'is_ldap_role' já existe na tabela Role")
            
            print("✅ Migração concluída com sucesso!")
            print("\n📋 Próximos passos:")
            print("1. Configure as variáveis LDAP no arquivo .env")
            print("2. Mapeie os grupos LDAP editando LDAP_ROLE_MAPPING em routes/auth.py") 
            print("3. Teste a conexão LDAP na página de configurações")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {e}")
            print("💡 Caso o erro persista, você pode recriar o banco:")
            print("   1. Exclua o arquivo instance/certificados.db")
            print("   2. Execute: python init_db.py")
            return False
            
    return True

if __name__ == "__main__":
    success = migrate_ldap_fields()
    sys.exit(0 if success else 1)