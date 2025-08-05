# routes/auth.py
"""Rotas de autenticação e login com suporte LDAP/AD melhorado."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import identity_changed, Identity
from werkzeug.security import check_password_hash
from models import User, Role, db
from ldap3 import Server, Connection, ALL, SIMPLE, SUBTREE
import os
import time
import re
from functools import lru_cache
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Cache para conexões LDAP (evita reconexões desnecessárias)
_ldap_connection_cache = {}
_cache_timeout = 300  # 5 minutos

# Mapeamento de grupos LDAP para roles do sistema
LDAP_ROLE_MAPPING = {
    'CN=Administradores,OU=Grupos,DC=empresa,DC=com': 'admin',
    'CN=Gestores,OU=Grupos,DC=empresa,DC=com': 'gestor',
    'CN=Usuarios,OU=Grupos,DC=empresa,DC=com': 'usuario'
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Tela de login com suporte a banco de dados e LDAP."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth_mode = current_app.config.get('AUTH_MODE', 'banco')
        
        user = User.query.filter_by(username=username).first()
        
        # Admin sempre autentica pelo banco
        if user and user.username == 'admin':
            if user.status != 'ativo':
                flash('Usuário admin inativo ou bloqueado.', 'danger')
                return render_template('login.html')
            if user.password and check_password_hash(user.password, password):
                login_user(user)
                identity_changed.send(current_app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha inválidos', 'danger')
                return render_template('login.html')
        
        # Autenticação por banco
        if auth_mode == 'banco':
            if user and user.status == 'ativo':
                if user.password and check_password_hash(user.password, password):
                    login_user(user)
                    identity_changed.send(current_app, identity=Identity(user.id))
                    return redirect(url_for('dashboard'))
                else:
                    flash('Usuário ou senha inválidos', 'danger')
            else:
                flash('Usuário não encontrado ou inativo', 'danger')
        
        # Autenticação LDAP
        elif auth_mode == 'ldap':
            if authenticate_ldap(username, password):
                # Buscar ou criar usuário no banco
                user = User.query.filter_by(username=username).first()
                if not user:
                    # Buscar dados completos do usuário LDAP
                    ldap_user_data = get_ldap_user_details(username)
                    if ldap_user_data:
                        # Criar usuário com dados reais do LDAP
                        user = User(
                            username=username,
                            nome=ldap_user_data.get('nome', username),
                            email=ldap_user_data.get('email', f"{username}@empresa.com"),
                            ldap_user=True
                        )
                        db.session.add(user)
                        db.session.commit()
                        
                        # Mapear grupos LDAP para roles
                        assign_ldap_roles(user, ldap_user_data.get('grupos', []))
                    else:
                        flash('Erro ao obter dados do usuário LDAP', 'danger')
                        return render_template('login.html')
                else:
                    # Usuário já existe - sincronizar dados do LDAP
                    if user.ldap_user:
                        sync_ldap_user_data(user, username)
                
                if user.status == 'ativo':
                    login_user(user)
                    identity_changed.send(current_app, identity=Identity(user.id))
                    return redirect(url_for('dashboard'))
                else:
                    flash('Usuário inativo ou bloqueado', 'danger')
            else:
                flash('Credenciais LDAP inválidas', 'danger')
        
        return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout do usuário."""
    logout_user()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('auth.login'))

@lru_cache(maxsize=10)
def get_ldap_server_config():
    """Cache das configurações LDAP para melhor performance."""
    return {
        'server': os.environ.get('LDAP_SERVER', 'ldap://localhost'),
        'port': int(os.environ.get('LDAP_PORT', 389)),
        'base_dn': os.environ.get('LDAP_BASE_DN', 'dc=empresa,dc=com'),
        'user_dn': os.environ.get('LDAP_USER_DN', 'ou=usuarios'),
        'user_attr': os.environ.get('LDAP_USER_ATTR', 'sAMAccountName'),
        'bind_dn': os.environ.get('LDAP_BIND_DN', ''),
        'bind_password': os.environ.get('LDAP_BIND_PASSWORD', ''),
        'email_attr': os.environ.get('LDAP_EMAIL_ATTR', 'mail'),
        'name_attr': os.environ.get('LDAP_NAME_ATTR', 'displayName'),
        'group_attr': os.environ.get('LDAP_GROUP_ATTR', 'memberOf'),
        'timeout': int(os.environ.get('LDAP_TIMEOUT', 10))
    }

def get_cached_ldap_connection():
    """Obtém conexão LDAP do cache ou cria nova."""
    config = get_ldap_server_config()
    cache_key = f"{config['server']}:{config['port']}"
    
    # Verificar cache
    if cache_key in _ldap_connection_cache:
        conn_data = _ldap_connection_cache[cache_key]
        if time.time() - conn_data['timestamp'] < _cache_timeout:
            if conn_data['connection'].bound:
                return conn_data['connection']
    
    # Criar nova conexão com timeout
    try:
        # Construir URL do servidor com validação
        server_url = config['server']
        if not server_url.startswith(('ldap://', 'ldaps://')):
            server_url = f"ldap://{server_url}"
        if ':' not in server_url.split('//')[-1]:
            server_url = f"{server_url}:{config['port']}"
        
        # Validar formato da URL
        if not re.match(r'^ldaps?://[\w\.-]+:\d+$', server_url):
            raise ValueError(f"URL LDAP inválida: {server_url}")
        
        server = Server(server_url, get_info=ALL, connect_timeout=config['timeout'])
        
        # Bind com retry
        for attempt in range(3):
            try:
                if config['bind_dn'] and config['bind_password']:
                    conn = Connection(
                        server, 
                        user=config['bind_dn'], 
                        password=config['bind_password'], 
                        authentication=SIMPLE,
                        auto_bind=True,
                        read_only=True,
                        receive_timeout=config['timeout']
                    )
                else:
                    conn = Connection(
                        server, 
                        auto_bind=True,
                        read_only=True,
                        receive_timeout=config['timeout']
                    )
                
                if conn.bound:
                    # Armazenar no cache
                    _ldap_connection_cache[cache_key] = {
                        'connection': conn,
                        'timestamp': time.time()
                    }
                    return conn
                break
                
            except Exception as e:
                if attempt == 2:  # Última tentativa
                    raise e
                time.sleep(1)  # Aguardar antes de retry
                
    except Exception as e:
        current_app.logger.error(f"Erro ao conectar LDAP: {e}")
        return None
    
    return None

def authenticate_ldap(username, password):
    """Autentica usuário via LDAP com melhorias de segurança e performance."""
    # Validação de entrada
    if not username or not password:
        current_app.logger.warning("Tentativa de login LDAP com credenciais vazias")
        return False
    
    # Sanitizar username
    username = re.sub(r'[^\w\.-]', '', username.strip().lower())
    if not username:
        current_app.logger.warning("Username LDAP inválido após sanitização")
        return False
    
    try:
        config = get_ldap_server_config()
        conn = get_cached_ldap_connection()
        
        if not conn:
            current_app.logger.error("Falha ao obter conexão LDAP")
            return False
        
        # Buscar usuário com atributos estendidos
        search_base = f"{config['user_dn']},{config['base_dn']}"
        search_filter = f"({config['user_attr']}={username})"
        attributes = [
            config['user_attr'], 
            config['email_attr'], 
            config['name_attr'],
            config['group_attr'],
            'userAccountControl'  # Para verificar se conta está ativa
        ]
        
        success = conn.search(
            search_base, 
            search_filter, 
            search_scope=SUBTREE,
            attributes=attributes
        )
        
        if not success or not conn.entries:
            current_app.logger.warning(f"Usuário LDAP não encontrado: {username}")
            return False
        
        user_entry = conn.entries[0]
        user_dn = user_entry.entry_dn
        
        # Verificar se conta está ativa (AD)
        if 'userAccountControl' in user_entry:
            uac = int(user_entry.userAccountControl.value)
            if uac & 0x0002:  # ACCOUNTDISABLE flag
                current_app.logger.warning(f"Conta LDAP desabilitada: {username}")
                return False
        
        # Tentar autenticação com timeout
        server = conn.server
        user_conn = Connection(
            server, 
            user=user_dn, 
            password=password, 
            authentication=SIMPLE,
            receive_timeout=config['timeout']
        )
        
        # Bind do usuário
        auth_success = user_conn.bind()
        
        if auth_success:
            current_app.logger.info(f"Autenticação LDAP bem-sucedida: {username}")
        else:
            current_app.logger.warning(f"Falha na autenticação LDAP: {username}")
        
        user_conn.unbind()
        return auth_success
        
    except Exception as e:
        current_app.logger.error(f"Erro na autenticação LDAP para {username}: {e}")
        return False

def get_ldap_user_details(username):
    """Obtém detalhes completos do usuário LDAP."""
    try:
        config = get_ldap_server_config()
        conn = get_cached_ldap_connection()
        
        if not conn:
            return None
        
        # Buscar dados completos do usuário
        search_base = f"{config['user_dn']},{config['base_dn']}"
        search_filter = f"({config['user_attr']}={username})"
        attributes = [
            config['user_attr'],
            config['email_attr'],
            config['name_attr'],
            config['group_attr'],
            'department',
            'title',
            'telephoneNumber'
        ]
        
        success = conn.search(search_base, search_filter, attributes=attributes)
        
        if success and conn.entries:
            entry = conn.entries[0]
            
            # Extrair grupos
            grupos = []
            if config['group_attr'] in entry:
                grupos = [str(group) for group in entry[config['group_attr']].values]
            
            return {
                'nome': str(entry[config['name_attr']].value) if config['name_attr'] in entry else username,
                'email': str(entry[config['email_attr']].value) if config['email_attr'] in entry else f"{username}@empresa.com",
                'grupos': grupos,
                'departamento': str(entry['department'].value) if 'department' in entry else '',
                'cargo': str(entry['title'].value) if 'title' in entry else '',
                'telefone': str(entry['telephoneNumber'].value) if 'telephoneNumber' in entry else ''
            }
            
    except Exception as e:
        current_app.logger.error(f"Erro ao obter detalhes LDAP de {username}: {e}")
    
    return None

def assign_ldap_roles(user, ldap_groups):
    """Mapeia grupos LDAP para roles do sistema."""
    try:
        # Remover roles LDAP existentes
        user.roles = [role for role in user.roles if not role.is_ldap_role]
        
        # Mapear novos grupos
        for group_dn in ldap_groups:
            if group_dn in LDAP_ROLE_MAPPING:
                role_name = LDAP_ROLE_MAPPING[group_dn]
                role = Role.query.filter_by(nome=role_name).first()  # Usar 'nome' em vez de 'name'
                if role and role not in user.roles:
                    user.roles.append(role)
                    current_app.logger.info(f"Role '{role_name}' atribuída ao usuário {user.username} via LDAP")
        
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Erro ao mapear roles LDAP para {user.username}: {e}")

def sync_ldap_user_data(user, username):
    """Sincroniza dados do usuário LDAP a cada login."""
    try:
        # Verificar se última sincronização foi há mais de 1 hora
        if hasattr(user, 'last_ldap_sync'):
            if user.last_ldap_sync and (datetime.now() - user.last_ldap_sync).seconds < 3600:
                return  # Não sincronizar muito frequentemente
        
        ldap_data = get_ldap_user_details(username)
        if ldap_data:
            # Atualizar dados do usuário
            user.nome = ldap_data.get('nome', user.nome)
            user.email = ldap_data.get('email', user.email)
            
            # Atualizar roles baseadas em grupos
            assign_ldap_roles(user, ldap_data.get('grupos', []))
            
            # Marcar timestamp da sincronização
            user.last_ldap_sync = datetime.now()
            
            db.session.commit()
            current_app.logger.info(f"Dados LDAP sincronizados para {username}")
            
    except Exception as e:
        current_app.logger.error(f"Erro ao sincronizar dados LDAP de {username}: {e}") 