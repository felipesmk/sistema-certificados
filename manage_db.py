#!/usr/bin/env python3
"""
🗄️ SISTEMA UNIFICADO DE GESTÃO DE BANCO DE DADOS
=================================================

Script principal para todas as operações de banco de dados:
- Inicialização e reset
- Migrações e upgrades
- Criação de usuários
- Backup e restore
- Diagnósticos e validação

Uso: python manage_db.py [comando] [opções]
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, Permission, RolePermission, RoleHistory, RoleTemplate
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text

class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}[DB] {text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.ENDC}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"{Colors.CYAN}[INFO] {text}{Colors.ENDC}")

class DatabaseManager:
    """Gerenciador principal do banco de dados"""
    
    def __init__(self):
        # Detectar tipo de banco
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print_warning("DATABASE_URL não encontrada no ambiente!")
            print_info("Execute: python configure_postgresql.py")
            print_info("Ou configure manualmente o arquivo .env")
            sys.exit(1)
            
        if db_url.startswith('postgresql://'):
            self.db_type = 'postgresql'
            self.db_path = None  # PostgreSQL não usa arquivo local
        else:
            # Fallback para SQLite apenas em desenvolvimento
            self.db_type = 'sqlite'
            self.db_path = os.path.join(app.instance_path, 'certificados.db')
        
        self.backup_dir = Path('backups')
        self.backup_dir.mkdir(exist_ok=True)
    
    def init_database(self, reset=False):
        """Inicializa o banco de dados"""
        print_header("INICIALIZAÇÃO DO BANCO DE DADOS")
        
        with app.app_context():
            if self.db_type == 'sqlite' and reset and os.path.exists(self.db_path):
                print_warning("Removendo banco SQLite existente...")
                os.remove(self.db_path)
                print_success("Banco removido")
            elif self.db_type == 'postgresql' and reset:
                print_warning("Reset do PostgreSQL - removendo todas as tabelas...")
                db.drop_all()
                print_success("Tabelas removidas")
            
            # Criar todas as tabelas
            print_info("Criando estrutura do banco...")
            db.create_all()
            print_success("Tabelas criadas")
            
            # Criar permissões padrão
            self._create_default_permissions()
            
            # Criar roles padrão
            self._create_default_roles()
            
            # Criar templates padrão
            self._create_default_templates()
            
            print_success("Banco inicializado com sucesso!")
    
    def _create_default_permissions(self):
        """Cria permissões padrão do sistema"""
        print_info("Criando permissões padrão...")
        
        permissions_data = [
            {
                'nome': 'manage_access',
                'descricao': 'Gerenciar usuários e perfis',
                'categoria': 'sistema',
                'criticidade': 'critica',
                'recurso': 'usuarios',
                'acao': 'manage'
            },
            {
                'nome': 'manage_registros',
                'descricao': 'Gerenciar registros de certificados',
                'categoria': 'dados',
                'criticidade': 'alta',
                'recurso': 'registros',
                'acao': 'manage'
            },
            {
                'nome': 'manage_responsaveis',
                'descricao': 'Gerenciar responsáveis',
                'categoria': 'dados',
                'criticidade': 'media',
                'recurso': 'responsaveis',
                'acao': 'manage'
            },
            {
                'nome': 'manage_config',
                'descricao': 'Gerenciar configurações do sistema',
                'categoria': 'sistema',
                'criticidade': 'critica',
                'recurso': 'configuracoes',
                'acao': 'manage'
            },
            {
                'nome': 'send_alerts',
                'descricao': 'Enviar alertas por email',
                'categoria': 'comunicacao',
                'criticidade': 'media',
                'recurso': 'emails',
                'acao': 'send'
            }
        ]
        
        for perm_data in permissions_data:
            perm = Permission.query.filter_by(nome=perm_data['nome']).first()
            if not perm:
                perm = Permission(**perm_data)
                db.session.add(perm)
                print_success(f"Permissão '{perm_data['nome']}' criada")
        
        db.session.commit()
    
    def _create_default_roles(self):
        """Cria roles padrão do sistema"""
        print_info("Criando roles padrão...")
        
        roles_data = [
            {
                'nome': 'admin',
                'descricao': 'Administrador do sistema',
                'cor': '#dc3545',
                'icone': 'bi-shield-fill',
                'prioridade': 10,
                'permissions': ['manage_access', 'manage_registros', 'manage_responsaveis', 'manage_config', 'send_alerts']
            },
            {
                'nome': 'operador',
                'descricao': 'Operador do sistema',
                'cor': '#0d6efd',
                'icone': 'bi-gear',
                'prioridade': 5,
                'permissions': ['manage_registros', 'manage_responsaveis', 'send_alerts']
            },
            {
                'nome': 'visualizador',
                'descricao': 'Visualizador de dados',
                'cor': '#6c757d',
                'icone': 'bi-eye',
                'prioridade': 1,
                'permissions': []
            }
        ]
        
        for role_data in roles_data:
            role = Role.query.filter_by(nome=role_data['nome']).first()
            if not role:
                # Criar role
                role = Role(
                    nome=role_data['nome'],
                    descricao=role_data['descricao'],
                    cor=role_data.get('cor', '#6c757d'),
                    icone=role_data.get('icone', 'bi-person'),
                    prioridade=role_data.get('prioridade', 0),
                    ativo=True,
                    created_by='system'
                )
                db.session.add(role)
                db.session.flush()  # Para obter o ID
                
                # Adicionar permissões
                for perm_nome in role_data['permissions']:
                    perm = Permission.query.filter_by(nome=perm_nome).first()
                    if perm:
                        role.permissions.append(perm)
                
                print_success(f"Role '{role_data['nome']}' criada com {len(role_data['permissions'])} permissões")
        
        db.session.commit()
    
    def _create_default_templates(self):
        """Cria templates padrão"""
        print_info("Criando templates padrão...")
        
        templates_data = [
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
        
        for template_data in templates_data:
            template = RoleTemplate.query.filter_by(nome=template_data['nome']).first()
            if not template:
                template = RoleTemplate(
                    nome=template_data['nome'],
                    descricao=template_data['descricao'],
                    categoria=template_data['categoria'],
                    config_json=json.dumps(template_data['config']),
                    ativo=True
                )
                db.session.add(template)
                print_success(f"Template '{template_data['nome']}' criado")
        
        db.session.commit()
    
    def create_user(self, username, nome, email, password, role_name='operador', interactive=False):
        """Cria um novo usuário"""
        print_header("CRIAÇÃO DE USUÁRIO")
        
        with app.app_context():
            # Verificar se usuário existe
            if User.query.filter_by(username=username).first():
                print_error(f"Usuário '{username}' já existe!")
                return False
            
            # Buscar role
            role = Role.query.filter_by(nome=role_name).first()
            if not role:
                print_error(f"Role '{role_name}' não encontrada!")
                return False
            
            try:
                user = User(
                    username=username,
                    nome=nome,
                    email=email,
                    password=generate_password_hash(password),
                    status='ativo',
                    role_id=role.id,
                    ldap_user=False
                )
                db.session.add(user)
                db.session.commit()
                
                print_success(f"Usuário '{username}' criado com sucesso!")
                print_info(f"Role: {role.nome}")
                print_info(f"Email: {email}")
                return True
                
            except Exception as e:
                print_error(f"Erro ao criar usuário: {e}")
                db.session.rollback()
                return False
    
    def create_admin(self, force=False):
        """Cria usuário admin interativamente"""
        print_header("CRIAÇÃO DE ADMINISTRADOR")
        
        with app.app_context():
            # Verificar se admin já existe
            admin_exists = User.query.filter_by(username='admin').first()
            if admin_exists:
                print_warning("Usuário 'admin' já existe!")
                if force or not sys.stdin.isatty():
                    print_info("Modo não interativo - recriando admin...")
                    db.session.delete(admin_exists)
                else:
                    overwrite = input("Deseja recriar? (s/N): ").lower().strip()
                    if overwrite != 's':
                        return False
                    else:
                        db.session.delete(admin_exists)
            
            # Dados padrão ou interativo
            if sys.stdin.isatty() and not force:  # Terminal interativo
                nome = input('Nome do admin (Admin): ').strip() or 'Admin'
                username = input('Username (admin): ').strip() or 'admin'
                email = input('Email (admin@admin.com): ').strip() or 'admin@admin.com'
                password = input('Senha (admin): ').strip() or 'admin'
            else:  # Script não interativo ou force
                nome = 'Admin'
                username = 'admin'
                email = 'admin@admin.com'
                password = 'admin'
                print_info(f"Criando admin padrão: {username} / {password}")
            
            return self.create_user(username, nome, email, password, 'admin')
    
    def backup_database(self):
        """Cria backup do banco de dados"""
        print_header("BACKUP DO BANCO DE DADOS")
        
        if self.db_type == 'sqlite' and not os.path.exists(self.db_path):
            print_error("Banco SQLite não encontrado!")
            return False
        elif self.db_type == 'postgresql':
            # Verificar conexão PostgreSQL
            try:
                db.session.execute(text("SELECT 1"))
            except Exception as e:
                print_error(f"Conexão PostgreSQL falhou: {e}")
                return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if self.db_type == 'sqlite':
                backup_file = self.backup_dir / f"certificados_backup_{timestamp}.db"
                shutil.copy2(self.db_path, backup_file)
                print_success(f"Backup criado: {backup_file}")
                
                # Manter apenas os 10 backups mais recentes
                backups = sorted(self.backup_dir.glob("certificados_backup_*.db"))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_backup.unlink()
                        print_info(f"Backup antigo removido: {old_backup.name}")
                
            elif self.db_type == 'postgresql':
                backup_file = self.backup_dir / f"certificados_backup_{timestamp}.sql"
                
                # Extrair informações da URL do PostgreSQL
                db_url = os.environ.get('DATABASE_URL', 'postgresql://certificados_user:certificados123@localhost:5432/certificados_db')
                
                # Parse da URL (formato: postgresql://user:pass@host:port/db)
                if db_url.startswith('postgresql://'):
                    parts = db_url.replace('postgresql://', '').split('@')
                    if len(parts) == 2:
                        user_pass = parts[0].split(':')
                        host_db = parts[1].split('/')
                        if len(user_pass) >= 2 and len(host_db) >= 2:
                            username = user_pass[0]
                            password = user_pass[1]
                            host_port = host_db[0].split(':')
                            host = host_port[0]
                            port = host_port[1] if len(host_port) > 1 else '5432'
                            database = host_db[1]
                            
                            # Usar pg_dump via subprocess
                            import subprocess
                            cmd = [
                                'pg_dump',
                                '-h', host,
                                '-p', port,
                                '-U', username,
                                '-d', database,
                                '-f', str(backup_file)
                            ]
                            
                            # Definir variável de ambiente para senha
                            env = os.environ.copy()
                            env['PGPASSWORD'] = password
                            
                            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                print_success(f"Backup PostgreSQL criado: {backup_file}")
                                
                                # Manter apenas os 10 backups mais recentes
                                backups = sorted(self.backup_dir.glob("certificados_backup_*.sql"))
                                if len(backups) > 10:
                                    for old_backup in backups[:-10]:
                                        old_backup.unlink()
                                        print_info(f"Backup antigo removido: {old_backup.name}")
                            else:
                                print_error(f"Erro no pg_dump: {result.stderr}")
                                return False
                        else:
                            print_error("Formato de URL PostgreSQL inválido")
                            return False
                    else:
                        print_error("Formato de URL PostgreSQL inválido")
                        return False
                else:
                    print_error("URL PostgreSQL inválida")
                    return False
            
            return str(backup_file)
            
        except Exception as e:
            print_error(f"Erro ao criar backup: {e}")
            return False
    
    def restore_database(self, backup_file):
        """Restaura banco de dados do backup"""
        print_header("RESTAURAÇÃO DO BANCO DE DADOS")
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print_error(f"Arquivo de backup não encontrado: {backup_file}")
            return False
        
        try:
            # Criar backup atual antes de restaurar
            current_backup = self.backup_database()
            if current_backup:
                print_info(f"Backup atual criado: {current_backup}")
            
            if self.db_type == 'sqlite':
                shutil.copy2(backup_path, self.db_path)
            elif self.db_type == 'postgresql':
                print_warning("Restauração do PostgreSQL não suportada via script. Use um cliente de restauração.")
                return False
            
            print_success(f"Banco restaurado de: {backup_file}")
            return True
            
        except Exception as e:
            print_error(f"Erro ao restaurar banco: {e}")
            return False
    
    def migrate_database(self):
        """Executa todas as migrações necessárias"""
        print_header("MIGRAÇÃO DO BANCO DE DADOS")
        
        with app.app_context():
            try:
                # Verificar se migrações são necessárias
                inspector = inspect(db.engine)
                
                # Lista de migrações
                migrations = [
                    self._migrate_ldap_fields,
                    self._migrate_advanced_roles,
                    self._migrate_user_fields,
                    self._migrate_indexes
                ]
                
                for migration in migrations:
                    migration(inspector)
                
                print_success("Todas as migrações executadas com sucesso!")
                return True
                
            except Exception as e:
                print_error(f"Erro na migração: {e}")
                return False
    
    def _migrate_ldap_fields(self, inspector):
        """Migração dos campos LDAP"""
        print_info("Verificando migração LDAP...")
        
        # Verificar User
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        if 'last_ldap_sync' not in user_columns:
            print_info("Adicionando campo last_ldap_sync...")
            db.session.execute(text("ALTER TABLE user ADD COLUMN last_ldap_sync DATETIME"))
        
        # Verificar Role
        role_columns = [col['name'] for col in inspector.get_columns('role')]
        if 'is_ldap_role' not in role_columns:
            print_info("Adicionando campo is_ldap_role...")
            db.session.execute(text("ALTER TABLE role ADD COLUMN is_ldap_role BOOLEAN DEFAULT 0"))
        
        db.session.commit()
        print_success("Migração LDAP concluída")
    
    def _migrate_advanced_roles(self, inspector):
        """Migração dos campos avançados de roles"""
        print_info("Verificando migração de roles avançados...")
        
        role_columns = [col['name'] for col in inspector.get_columns('role')]
        
        advanced_fields = [
            ('ativo', 'BOOLEAN DEFAULT 1'),
            ('cor', 'VARCHAR(7) DEFAULT "#6c757d"'),
            ('icone', 'VARCHAR(50) DEFAULT "bi-person"'),
            ('prioridade', 'INTEGER DEFAULT 0'),
            ('parent_id', 'INTEGER'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('created_by', 'VARCHAR(50)')
        ]
        
        for field_name, field_def in advanced_fields:
            if field_name not in role_columns:
                print_info(f"Adicionando campo {field_name}...")
                db.session.execute(text(f"ALTER TABLE role ADD COLUMN {field_name} {field_def}"))
        
        # Verificar Permission
        perm_columns = [col['name'] for col in inspector.get_columns('permission')]
        
        perm_fields = [
            ('categoria', 'VARCHAR(50) DEFAULT "geral"'),
            ('criticidade', 'VARCHAR(20) DEFAULT "media"'),
            ('recurso', 'VARCHAR(50)'),
            ('acao', 'VARCHAR(50)'),
            ('ativo', 'BOOLEAN DEFAULT 1'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for field_name, field_def in perm_fields:
            if field_name not in perm_columns:
                print_info(f"Adicionando campo {field_name} em Permission...")
                db.session.execute(text(f"ALTER TABLE permission ADD COLUMN {field_name} {field_def}"))
        
        db.session.commit()
        print_success("Migração de roles avançados concluída")
    
    def _migrate_user_fields(self, inspector):
        """Migração dos campos avançados de usuários"""
        print_info("Verificando migração de usuários avançados...")
        
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        
        user_fields = [
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ('last_login', 'DATETIME'),
            ('login_count', 'INTEGER DEFAULT 0'),
            ('telefone', 'VARCHAR(20)'),
            ('departamento', 'VARCHAR(100)'),
            ('cargo', 'VARCHAR(100)'),
            ('observacoes', 'TEXT'),
            ('created_by', 'VARCHAR(80)')
        ]
        
        for field_name, field_def in user_fields:
            if field_name not in user_columns:
                print_info(f"Adicionando campo {field_name} em User...")
                db.session.execute(text(f"ALTER TABLE user ADD COLUMN {field_name} {field_def}"))
        
        # Criar tabela UserHistory se não existir
        if not inspector.has_table('user_history'):
            print_info("Criando tabela user_history...")
            from models import UserHistory
            UserHistory.__table__.create(db.engine)
            print_success("Tabela user_history criada")
        
        # Atualizar registros existentes
        users = User.query.all()
        for user in users:
            if not hasattr(user, 'created_at') or user.created_at is None:
                user.created_at = datetime.now()
            if not hasattr(user, 'updated_at') or user.updated_at is None:
                user.updated_at = datetime.now()
            if not hasattr(user, 'login_count') or user.login_count is None:
                user.login_count = 0
        
        db.session.commit()
        print_success("Migração de usuários avançados concluída")
    
    def _migrate_indexes(self, inspector):
        """Cria índices para performance"""
        print_info("Verificando índices...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS ix_role_ativo ON role (ativo)",
            "CREATE INDEX IF NOT EXISTS ix_role_prioridade ON role (prioridade)",
            "CREATE INDEX IF NOT EXISTS ix_permission_categoria ON permission (categoria)",
            "CREATE INDEX IF NOT EXISTS ix_permission_ativo ON permission (ativo)"
        ]
        
        for index_sql in indexes:
            try:
                db.session.execute(text(index_sql))
            except Exception:
                pass  # Índice já existe
        
        db.session.commit()
        print_success("Índices verificados")
    
    def status(self):
        """Mostra status do banco de dados"""
        print_header("STATUS DO BANCO DE DADOS")
        
        if self.db_type == 'sqlite' and not os.path.exists(self.db_path):
            print_error("Banco SQLite não encontrado!")
            return
        elif self.db_type == 'postgresql':
            # Verificar conexão PostgreSQL
            try:
                db.session.execute(text("SELECT 1"))
            except Exception as e:
                print_error(f"Conexão PostgreSQL falhou: {e}")
                return
        
        with app.app_context():
            try:
                # Informações básicas
                if self.db_type == 'sqlite':
                    file_size = os.path.getsize(self.db_path) / 1024 / 1024  # MB
                    print_info(f"Arquivo: {self.db_path}")
                    print_info(f"Tamanho: {file_size:.2f} MB")
                elif self.db_type == 'postgresql':
                    print_info("Status do PostgreSQL (via conexão):")
                    try:
                        # Tentar uma consulta simples para verificar a conexão
                        db.session.execute(text("SELECT 1"))
                        print_success("Conexão PostgreSQL: OK")
                    except Exception as e:
                        print_error(f"Conexão PostgreSQL: Falha - {e}")
                
                # Contadores
                users_count = User.query.count()
                roles_count = Role.query.count()
                perms_count = Permission.query.count()
                templates_count = RoleTemplate.query.count()
                
                # Verificar campos avançados de usuários
                inspector = inspect(db.engine)
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                has_advanced_fields = all(field in user_columns for field in ['created_at', 'telefone', 'departamento'])
                has_user_history = inspector.has_table('user_history')
                
                print_info(f"Usuários: {users_count}")
                print_info(f"Roles: {roles_count}")
                print_info(f"Permissões: {perms_count}")
                print_info(f"Templates: {templates_count}")
                
                if has_advanced_fields:
                    print_success("Campos avançados de usuários: OK")
                else:
                    print_warning("Campos avançados de usuários: Pendente")
                
                if has_user_history:
                    print_success("Tabela UserHistory: OK")
                else:
                    print_warning("Tabela UserHistory: Pendente")
                
                # Verificar integridade
                admin_user = User.query.filter_by(username='admin').first()
                admin_role = Role.query.filter_by(nome='admin').first()
                
                print_success("Banco de dados operacional")
                if admin_user:
                    print_success("Usuário admin encontrado")
                else:
                    print_warning("Usuário admin não encontrado")
                
                if admin_role:
                    print_success("Role admin encontrada")
                else:
                    print_warning("Role admin não encontrada")
                
            except Exception as e:
                print_error(f"Erro ao verificar status: {e}")

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(
        description='🗄️ Sistema Unificado de Gestão de Banco de Dados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python manage_db.py init                    # Inicializar banco novo
  python manage_db.py reset                   # Reset completo do banco
  python manage_db.py create-admin            # Criar usuário admin
  python manage_db.py create-user user1 "Nome" email@test.com senha123
  python manage_db.py migrate                 # Executar migrações
  python manage_db.py backup                  # Criar backup
  python manage_db.py restore backup.db       # Restaurar backup
  python manage_db.py status                  # Ver status do banco
        """
    )
    
    parser.add_argument('command', 
                       choices=['init', 'reset', 'create-admin', 'create-user', 'migrate', 'backup', 'restore', 'status'],
                       help='Comando a executar')
    
    parser.add_argument('args', nargs='*', help='Argumentos do comando')
    parser.add_argument('--username', help='Nome de usuário')
    parser.add_argument('--name', help='Nome completo')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--password', help='Senha')
    parser.add_argument('--role', default='operador', help='Role do usuário')
    parser.add_argument('--force', action='store_true', help='Força operações sem confirmação')
    parser.add_argument('--non-interactive', action='store_true', help='Modo não interativo para scripts')
    
    args = parser.parse_args()
    
    # Criar instância do gerenciador
    db_manager = DatabaseManager()
    
    try:
        if args.command == 'init':
            db_manager.init_database(reset=False)
            
        elif args.command == 'reset':
            if args.force:
                print_warning("Reset forçado - removendo banco existente...")
                db_manager.init_database(reset=True)
                # Não criar admin automaticamente no reset --force
                print_info("Banco resetado. Use 'create-admin' para criar o administrador.")
            else:
                confirm = input("⚠️  Tem certeza que deseja RESETAR o banco? (digite 'RESET'): ")
                if confirm == 'RESET':
                    db_manager.init_database(reset=True)
                    db_manager.create_admin()
                else:
                    print_warning("Operação cancelada")
                
        elif args.command == 'create-admin':
            if args.non_interactive or args.force:
                # Modo não interativo - usar dados padrão
                db_manager.create_admin(force=True)
            else:
                db_manager.create_admin()
            
        elif args.command == 'create-user':
            if len(args.args) >= 4:
                username, name, email, password = args.args[:4]
                role = args.args[4] if len(args.args) > 4 else args.role
                db_manager.create_user(username, name, email, password, role)
            else:
                print_error("Uso: python manage_db.py create-user <username> <nome> <email> <senha> [role]")
                
        elif args.command == 'migrate':
            db_manager.migrate_database()
            
        elif args.command == 'backup':
            backup_file = db_manager.backup_database()
            if backup_file:
                print_info(f"Backup salvo em: {backup_file}")
                
        elif args.command == 'restore':
            if args.args:
                db_manager.restore_database(args.args[0])
            else:
                print_error("Uso: python manage_db.py restore <arquivo_backup>")
                
        elif args.command == 'status':
            db_manager.status()
            
    except KeyboardInterrupt:
        print_warning("\nOperação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()