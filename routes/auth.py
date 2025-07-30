# routes/auth.py
"""Rotas de autenticação e login."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_principal import identity_changed, Identity
from werkzeug.security import check_password_hash
from models import User, db
from ldap3 import Server, Connection, ALL, SIMPLE
import os

auth_bp = Blueprint('auth', __name__)

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
                    # Criar usuário do LDAP no banco
                    user = User(
                        username=username,
                        nome=username,  # Pode ser melhorado buscando do LDAP
                        email=f"{username}@empresa.com",  # Pode ser melhorado
                        ldap_user=True
                    )
                    db.session.add(user)
                    db.session.commit()
                
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

def authenticate_ldap(username, password):
    """Autentica usuário via LDAP."""
    try:
        ldap_server = os.environ.get('LDAP_SERVER', 'ldap://localhost')
        ldap_port = int(os.environ.get('LDAP_PORT', 389))
        ldap_base_dn = os.environ.get('LDAP_BASE_DN', 'dc=empresa,dc=com')
        ldap_user_dn = os.environ.get('LDAP_USER_DN', 'ou=usuarios')
        ldap_user_attr = os.environ.get('LDAP_USER_ATTR', 'sAMAccountName')
        ldap_bind_dn = os.environ.get('LDAP_BIND_DN', '')
        ldap_bind_password = os.environ.get('LDAP_BIND_PASSWORD', '')
        
        # Construir URL do servidor
        if ldap_server.startswith('ldap://') or ldap_server.startswith('ldaps://'):
            server_url = f"{ldap_server}:{ldap_port}"
        else:
            server_url = f"ldap://{ldap_server}:{ldap_port}"
        
        server = Server(server_url, get_info=ALL)
        
        # Bind com credenciais específicas ou anônimo
        if ldap_bind_dn and ldap_bind_password:
            conn = Connection(server, user=ldap_bind_dn, password=ldap_bind_password, authentication=SIMPLE, auto_bind=True)
        else:
            conn = Connection(server, auto_bind=True)
        
        if not conn.bound:
            return False
        
        # Buscar usuário
        search_base = f"{ldap_user_dn},{ldap_base_dn}"
        search_filter = f"({ldap_user_attr}={username})"
        
        conn.search(search_base, search_filter, attributes=[ldap_user_attr])
        
        if not conn.entries:
            return False
        
        user_dn = conn.entries[0].entry_dn
        
        # Tentar bind com credenciais do usuário
        user_conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE, auto_bind=True)
        
        return user_conn.bound
        
    except Exception as e:
        current_app.logger.error(f"Erro na autenticação LDAP: {e}")
        return False 