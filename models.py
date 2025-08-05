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
    """Perfil de acesso do sistema com funcionalidades avançadas.
    As permissões são associadas ao Role.
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descricao = db.Column(db.String(200))
    is_ldap_role = db.Column(db.Boolean, default=False, index=True)  # Role mapeada do LDAP
    
    # Funcionalidades avançadas
    ativo = db.Column(db.Boolean, default=True, index=True)  # Role ativo/inativo
    cor = db.Column(db.String(7), default='#6c757d')  # Cor para identificação visual
    icone = db.Column(db.String(50), default='bi-person')  # Ícone Bootstrap
    prioridade = db.Column(db.Integer, default=0, index=True)  # Para hierarquia
    parent_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)  # Role pai
    
    # Metadados
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(db.String(50))  # Usuário que criou
    
    # Relacionamentos
    permissions = db.relationship('Permission', secondary='role_permission', backref='roles', lazy='joined')
    children = db.relationship('Role', backref=db.backref('parent', remote_side=[id]))
    
    def get_all_permissions(self):
        """Retorna todas as permissões incluindo as herdadas do role pai."""
        perms = set(self.permissions)
        if self.parent:
            perms.update(self.parent.get_all_permissions())
        return list(perms)
    
    def can_be_deleted(self):
        """Verifica se o role pode ser excluído."""
        # Não pode excluir admin, roles em uso ou com filhos
        if self.nome == 'admin':
            return False, "Role 'admin' não pode ser excluído"
        if User.query.filter_by(role_id=self.id).count() > 0:
            return False, "Role está sendo usado por usuários"
        if len(self.children) > 0:
            return False, "Role possui sub-roles"
        return True, ""
    
    def to_dict(self):
        """Converte role para dicionário (para export/import)."""
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'icone': self.icone,
            'ativo': self.ativo,
            'prioridade': self.prioridade,
            'parent_nome': self.parent.nome if self.parent else None,
            'permissions': [p.nome for p in self.permissions]
        }

class Permission(db.Model):
    """Permissão de acesso granular com metadados avançados."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descricao = db.Column(db.String(200))
    
    # Funcionalidades avançadas
    categoria = db.Column(db.String(50), default='geral', index=True)  # Categoria da permissão
    criticidade = db.Column(db.String(20), default='media', index=True)  # baixa, media, alta, critica
    recurso = db.Column(db.String(50))  # Recurso que a permissão protege
    acao = db.Column(db.String(50))  # Ação permitida (create, read, update, delete)
    ativo = db.Column(db.Boolean, default=True, index=True)
    
    # Metadados
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        """Converte permissão para dicionário."""
        return {
            'nome': self.nome,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'criticidade': self.criticidade,
            'recurso': self.recurso,
            'acao': self.acao,
            'ativo': self.ativo
        }

class RolePermission(db.Model):
    """Associação N:N entre Role e Permission."""
    __tablename__ = 'role_permission'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), index=True)

class RoleHistory(db.Model):
    """Histórico de alterações em roles."""
    __tablename__ = 'role_history'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    acao = db.Column(db.String(50), nullable=False)  # created, updated, deleted, permissions_changed
    detalhes = db.Column(db.Text)  # JSON com detalhes da alteração
    usuario = db.Column(db.String(50), nullable=False)  # Usuário que fez a alteração
    timestamp = db.Column(db.DateTime, default=db.func.now())
    
    role = db.relationship('Role', backref=db.backref('history', cascade='all, delete-orphan'))

class RoleTemplate(db.Model):
    """Templates predefinidos de roles para criação rápida."""
    __tablename__ = 'role_template'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.String(200))
    categoria = db.Column(db.String(50), default='personalizado')
    config_json = db.Column(db.Text)  # JSON com configuração do template
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

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
    last_ldap_sync = db.Column(db.DateTime)  # Timestamp da última sincronização LDAP
    
    # Campos adicionais para gestão avançada
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    telefone = db.Column(db.String(20))
    departamento = db.Column(db.String(100))
    cargo = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    created_by = db.Column(db.String(80))
    
    def to_dict(self):
        """Converte usuário para dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'nome': self.nome,
            'email': self.email,
            'status': self.status,
            'role_name': self.role.nome if self.role else None,
            'ldap_user': self.ldap_user,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'telefone': self.telefone,
            'departamento': self.departamento,
            'cargo': self.cargo,
            'login_count': self.login_count
        }
    
    def can_be_deleted(self):
        """Verifica se o usuário pode ser deletado"""
        return self.username != 'admin'

class UserHistory(db.Model):
    """Histórico de alterações dos usuários"""
    __tablename__ = 'user_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    acao = db.Column(db.String(50), nullable=False, index=True)  # 'created', 'updated', 'login', 'role_changed', 'status_changed', 'password_reset'
    detalhes = db.Column(db.Text)  # JSON com detalhes da alteração
    ip_address = db.Column(db.String(45))  # IPv4 ou IPv6
    user_agent = db.Column(db.String(255))
    usuario = db.Column(db.String(80), nullable=False, index=True)  # Quem fez a alteração
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False, index=True)
    
    # Relacionamento
    user = db.relationship('User', backref=db.backref('history', cascade='all, delete-orphan'))

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
