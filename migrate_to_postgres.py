#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from datetime import datetime
from pathlib import Path

# Configurações
SQLITE_DB = 'instance/certificados.db'
POSTGRES_URL = os.environ.get('DATABASE_URL', 'postgresql://certificados_user:certificados123@localhost:5432/certificados_db')

def migrate_data():
    """Migra dados do SQLite para PostgreSQL"""
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Banco SQLite não encontrado: {SQLITE_DB}")
        return False
    
    try:
        # Conectar ao SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        
        # Conectar ao PostgreSQL
        pg_conn = psycopg2.connect(POSTGRES_URL)
        pg_cursor = pg_conn.cursor()
        
        print("🔄 Iniciando migração de dados...")
        
        # Migrar tabelas na ordem correta (respeitando foreign keys)
        tables = [
            'permission',
            'role', 
            'role_permission',
            'user',
            'user_history',
            'role_history',
            'role_template',
            'responsavel',
            'registro',
            'registro_responsavel',
            'configuracao'
        ]
        
        for table in tables:
            print(f"🔄 Migrando tabela: {table}")
            
            # Verificar se tabela existe no SQLite
            sqlite_cursor = sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not sqlite_cursor.fetchone():
                print(f"⚠️  Tabela {table} não existe no SQLite, pulando...")
                continue
            
            # Buscar dados do SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"ℹ️  Tabela {table} está vazia, pulando...")
                continue
            
            # Inserir no PostgreSQL
            for row in rows:
                columns = list(row.keys())
                values = list(row)
                
                # Tratar tipos específicos
                for i, value in enumerate(values):
                    if isinstance(value, datetime):
                        values[i] = value.isoformat()
                    elif value == '':
                        values[i] = None
                    elif isinstance(value, int) and columns[i] in ['ativo', 'is_ldap_role', 'ldap_user', 'regularizado', 'agendamento_ativo']:
                        # Converter inteiros para boolean
                        values[i] = bool(value)
                
                placeholders = ', '.join(['%s'] * len(values))
                
                # Escapar nome da tabela se for palavra reservada
                table_name = f'"{table}"' if table.lower() in ['user', 'order', 'group'] else table
                columns_str = ', '.join([f'"{col}"' for col in columns])
                
                try:
                    pg_cursor.execute(
                        f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                        values
                    )
                except Exception as e:
                    print(f"❌ Erro ao inserir na tabela {table}: {e}")
                    print(f"   Dados: {dict(row)}")
                    # Rollback e continuar com próxima linha
                    pg_conn.rollback()
                    continue
            
            print(f"✅ {len(rows)} registros migrados para {table}")
        
        # Commit das alterações
        pg_conn.commit()
        
        print("✅ Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        if 'pg_conn' in locals():
            pg_conn.rollback()
        return False
        
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == '__main__':
    migrate_data()
