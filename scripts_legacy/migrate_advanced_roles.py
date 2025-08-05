#!/usr/bin/env python3
"""
Script de migração para adicionar funcionalidades avançadas de roles.
Execute após ativar o ambiente virtual.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Role, Permission, RoleHistory, RoleTemplate
from sqlalchemy import text
from datetime import datetime

def migrate_advanced_roles():
    """Adiciona funcionalidades avançadas de roles ao banco de dados."""
    print("🚀 Iniciando migração das funcionalidades avançadas de roles...")
    
    with app.app_context():
        try:
            # Verificar se as colunas já existem
            inspector = db.inspect(db.engine)
            
            # 1. Adicionar campos avançados na tabela Role
            role_columns = [col['name'] for col in inspector.get_columns('role')]
            
            new_role_fields = [
                ('ativo', 'BOOLEAN DEFAULT 1'),
                ('cor', 'VARCHAR(7) DEFAULT "#6c757d"'),
                ('icone', 'VARCHAR(50) DEFAULT "bi-person"'),
                ('prioridade', 'INTEGER DEFAULT 0'),
                ('parent_id', 'INTEGER'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('created_by', 'VARCHAR(50)')
            ]
            
            for field_name, field_def in new_role_fields:
                if field_name not in role_columns:
                    print(f"➕ Adicionando campo '{field_name}' à tabela Role...")
                    db.engine.execute(text(f"ALTER TABLE role ADD COLUMN {field_name} {field_def}"))
                else:
                    print(f"✅ Campo '{field_name}' já existe na tabela Role")
            
            # 2. Adicionar campos avançados na tabela Permission
            perm_columns = [col['name'] for col in inspector.get_columns('permission')]
            
            new_perm_fields = [
                ('categoria', 'VARCHAR(50) DEFAULT "geral"'),
                ('criticidade', 'VARCHAR(20) DEFAULT "media"'),
                ('recurso', 'VARCHAR(50)'),
                ('acao', 'VARCHAR(50)'),
                ('ativo', 'BOOLEAN DEFAULT 1'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for field_name, field_def in new_perm_fields:
                if field_name not in perm_columns:
                    print(f"➕ Adicionando campo '{field_name}' à tabela Permission...")
                    db.engine.execute(text(f"ALTER TABLE permission ADD COLUMN {field_name} {field_def}"))
                else:
                    print(f"✅ Campo '{field_name}' já existe na tabela Permission")
            
            # 3. Criar tabela RoleHistory
            if 'role_history' not in inspector.get_table_names():
                print("➕ Criando tabela RoleHistory...")
                db.engine.execute(text("""
                    CREATE TABLE role_history (
                        id INTEGER PRIMARY KEY,
                        role_id INTEGER NOT NULL,
                        acao VARCHAR(50) NOT NULL,
                        detalhes TEXT,
                        usuario VARCHAR(50) NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (role_id) REFERENCES role (id)
                    )
                """))
            else:
                print("✅ Tabela RoleHistory já existe")
            
            # 4. Criar tabela RoleTemplate
            if 'role_template' not in inspector.get_table_names():
                print("➕ Criando tabela RoleTemplate...")
                db.engine.execute(text("""
                    CREATE TABLE role_template (
                        id INTEGER PRIMARY KEY,
                        nome VARCHAR(50) UNIQUE NOT NULL,
                        descricao VARCHAR(200),
                        categoria VARCHAR(50) DEFAULT 'personalizado',
                        config_json TEXT,
                        ativo BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:
                print("✅ Tabela RoleTemplate já existe")
            
            # 5. Criar índices para melhor performance
            print("📈 Criando índices...")
            indices = [
                "CREATE INDEX IF NOT EXISTS ix_role_ativo ON role (ativo)",
                "CREATE INDEX IF NOT EXISTS ix_role_prioridade ON role (prioridade)",
                "CREATE INDEX IF NOT EXISTS ix_permission_categoria ON permission (categoria)",
                "CREATE INDEX IF NOT EXISTS ix_permission_ativo ON permission (ativo)",
                "CREATE INDEX IF NOT EXISTS ix_role_history_role_id ON role_history (role_id)",
                "CREATE INDEX IF NOT EXISTS ix_role_history_timestamp ON role_history (timestamp)"
            ]
            
            for index_sql in indices:
                try:
                    db.engine.execute(text(index_sql))
                except Exception as e:
                    print(f"⚠️  Índice já existe ou erro: {e}")
            
            # 6. Atualizar dados existentes
            print("🔄 Atualizando dados existentes...")
            
            # Atualizar roles existentes com valores padrão
            existing_roles = Role.query.all()
            for role in existing_roles:
                if not hasattr(role, 'ativo') or role.ativo is None:
                    role.ativo = True
                if not hasattr(role, 'cor') or not role.cor:
                    role.cor = '#6c757d'
                if not hasattr(role, 'icone') or not role.icone:
                    role.icone = 'bi-person'
                if not hasattr(role, 'prioridade') or role.prioridade is None:
                    role.prioridade = 0
                if not hasattr(role, 'created_at') or not role.created_at:
                    role.created_at = datetime.now()
                if not hasattr(role, 'updated_at') or not role.updated_at:
                    role.updated_at = datetime.now()
            
            # Atualizar permissões existentes
            existing_perms = Permission.query.all()
            perm_categories = {
                'manage_access': {'categoria': 'sistema', 'criticidade': 'critica', 'recurso': 'usuarios', 'acao': 'manage'},
                'manage_registros': {'categoria': 'dados', 'criticidade': 'alta', 'recurso': 'registros', 'acao': 'manage'},
                'manage_responsaveis': {'categoria': 'dados', 'criticidade': 'media', 'recurso': 'responsaveis', 'acao': 'manage'},
                'manage_config': {'categoria': 'sistema', 'criticidade': 'critica', 'recurso': 'configuracoes', 'acao': 'manage'},
                'send_alerts': {'categoria': 'comunicacao', 'criticidade': 'media', 'recurso': 'emails', 'acao': 'send'}
            }
            
            for perm in existing_perms:
                if perm.nome in perm_categories:
                    config = perm_categories[perm.nome]
                    if not hasattr(perm, 'categoria') or not perm.categoria:
                        perm.categoria = config['categoria']
                    if not hasattr(perm, 'criticidade') or not perm.criticidade:
                        perm.criticidade = config['criticidade']
                    if not hasattr(perm, 'recurso') or not perm.recurso:
                        perm.recurso = config['recurso']
                    if not hasattr(perm, 'acao') or not perm.acao:
                        perm.acao = config['acao']
                if not hasattr(perm, 'ativo') or perm.ativo is None:
                    perm.ativo = True
                if not hasattr(perm, 'created_at') or not perm.created_at:
                    perm.created_at = datetime.now()
            
            db.session.commit()
            
            # 7. Criar templates padrão
            print("📝 Criando templates padrão...")
            templates_padrão = [
                {
                    'nome': 'Administrador Departamental',
                    'descricao': 'Gerencia usuários e dados do departamento',
                    'categoria': 'gestao',
                    'config': {
                        'permissions': ['manage_registros', 'manage_responsaveis', 'send_alerts'],
                        'cor': '#28a745',
                        'icone': 'bi-building',
                        'prioridade': 5
                    }
                },
                {
                    'nome': 'Operador Sistema',
                    'descricao': 'Acesso operacional para tarefas diárias',
                    'categoria': 'operacional',
                    'config': {
                        'permissions': ['manage_registros', 'send_alerts'],
                        'cor': '#17a2b8',
                        'icone': 'bi-gear',
                        'prioridade': 3
                    }
                },
                {
                    'nome': 'Visualizador',
                    'descricao': 'Apenas leitura de dados e relatórios',
                    'categoria': 'consulta',
                    'config': {
                        'permissions': [],
                        'cor': '#6c757d',
                        'icone': 'bi-eye',
                        'prioridade': 1
                    }
                },
                {
                    'nome': 'Auditor',
                    'descricao': 'Acesso para auditoria e compliance',
                    'categoria': 'auditoria',
                    'config': {
                        'permissions': ['manage_access'],
                        'cor': '#fd7e14',
                        'icone': 'bi-shield-check',
                        'prioridade': 4
                    }
                }
            ]
            
            for template_data in templates_padrão:
                existing = RoleTemplate.query.filter_by(nome=template_data['nome']).first()
                if not existing:
                    template = RoleTemplate(
                        nome=template_data['nome'],
                        descricao=template_data['descricao'],
                        categoria=template_data['categoria'],
                        config_json=json.dumps(template_data['config']),
                        ativo=True
                    )
                    db.session.add(template)
                    print(f"✅ Template '{template_data['nome']}' criado")
                else:
                    print(f"✅ Template '{template_data['nome']}' já existe")
            
            db.session.commit()
            
            print("\n🎉 Migração concluída com sucesso!")
            print("\n📋 Novas funcionalidades disponíveis:")
            print("• Dashboard avançado de gestão de perfis")
            print("• Clonagem de perfis")
            print("• Ações em lote (ativar/desativar/excluir)")
            print("• Templates de perfis")
            print("• Assistente de criação")
            print("• Histórico de alterações")
            print("• Importação/exportação")
            print("• Hierarquia de perfis")
            print("• Relatórios de permissões")
            print("• Interface visual melhorada")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    return True

if __name__ == "__main__":
    success = migrate_advanced_roles()
    sys.exit(0 if success else 1)