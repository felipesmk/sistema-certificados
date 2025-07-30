# models.py
"""
Modelos principais do sistema: User, Role, Permission, etc.
Implementa o RBAC (Role-Based Access Control) e entidades de domínio.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Associação N:N entre Registro e Responsavel
registro_responsavel = db.Table(
    'registro_responsavel',
    db.Column('registro_id', db.Integer, db.ForeignKey('registro.id')),
    db.Column('responsavel_id', db.Integer, db.ForeignKey('responsavel.id'))
)

class Role(db.Model):
    """Perfil de acesso do sistema. Cada usuário tem um Role.
    As permissões são associadas ao Role.
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descricao = db.Column(db.String(200))
    # Permissões associadas ao perfil
    permissions = db.relationship('Permission', secondary='role_permission', backref='roles', lazy='joined')

class Permission(db.Model):
    """Permissão de acesso granular (ex: manage_access, manage_config, etc)."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descricao = db.Column(db.String(200))

class RolePermission(db.Model):
    """Associação N:N entre Role e Permission."""
    __tablename__ = 'role_permission'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), index=True)

class User(UserMixin, db.Model):
    """Usuário do sistema. Cada usuário tem um perfil (role).
    O admin SEMPRE deve ter o perfil admin.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=True)  # Pode ser null para LDAP
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='ativo', index=True)  # 'ativo', 'inativo', 'bloqueado'
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), index=True)
    # Perfil do usuário
    role = db.relationship('Role', backref='users', lazy='joined')
    ldap_user = db.Column(db.Boolean, default=False, index=True)

class Responsavel(db.Model):
    """Pessoa responsável por um registro."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)

    def __str__(self):
        return f"{self.nome} ({self.email})"

class Registro(db.Model):
    """Registro de certificado/documento controlado."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    origem = db.Column(db.String(120), nullable=True)
    tipo = db.Column(db.String(50), nullable=False, index=True)
    data_vencimento = db.Column(db.Date, nullable=False, index=True)
    tempo_alerta = db.Column(db.Integer, nullable=False, default=7)
    observacoes = db.Column(db.Text, nullable=True)
    regularizado = db.Column(db.Boolean, default=False, index=True)
    responsaveis = db.relationship('Responsavel', secondary=registro_responsavel, backref='registros')

    def __repr__(self):
        return f'<Registro {self.nome}>' 

class Configuracao(db.Model):
    """Configuração do sistema (agendamento, email, etc)."""
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(10), nullable=False, default='fri')  # Ex: 'mon', 'tue', ...
    hora = db.Column(db.Integer, nullable=False, default=14)
    minuto = db.Column(db.Integer, nullable=False, default=0)
    agendamento_ativo = db.Column(db.Boolean, default=True)  # Controla se o agendamento está ativo
    
    # Configurações de Email
    mail_server = db.Column(db.String(100), default='smtp.gmail.com')
    mail_port = db.Column(db.Integer, default=587)
    mail_username = db.Column(db.String(100))
    mail_password = db.Column(db.String(200))
    mail_use_tls = db.Column(db.String(10), default='tls')  # 'tls', 'ssl', 'none'
    mail_default_sender = db.Column(db.String(100))
    
    # Configurações de Personalização do Sistema (simplificadas)
    nome_sistema = db.Column(db.String(100), default='Sistema de Certificados')
    equipe_ti = db.Column(db.String(100), default='Equipe de TI')
    email_ti = db.Column(db.String(100), default='ti@empresa.com')
    telefone_ti = db.Column(db.String(20), default='(11) 99999-9999')
    logo_url = db.Column(db.String(200), default='')
