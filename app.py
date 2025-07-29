from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
import logging.handlers
from werkzeug.security import check_password_hash
from flask_mail import Mail, Message
import json
from datetime import date, timedelta, datetime
from wtforms.validators import ValidationError
from apscheduler.schedulers.background import BackgroundScheduler
import os
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE
from flask_principal import Principal, Permission, RoleNeed, UserNeed, identity_loaded, Identity, AnonymousIdentity, identity_changed, PermissionDenied, Need
from functools import wraps
from flask import abort
import secrets
from models import Role
from models import Permission

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Configuração de logging para produção
def setup_logging():
    """Configura logging para produção com rotação de arquivos"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    
    # Adicionar handler ao logger
    logger.addHandler(file_handler)
    
    # Log para console apenas em desenvolvimento
    if os.environ.get('FLASK_ENV') != 'production':
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

# Configurar logging
setup_logging()

# Configurações do Flask com suporte a variáveis de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///certificados.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de email
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 8025))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'  # Desabilitado para localhost
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'  # False para smtp4dev
app.config['MAIL_DEBUG'] = os.environ.get('MAIL_DEBUG', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'test@localhost')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'test@localhost')

# Configurações de sessão
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
)

# Configurações de autenticação
app.config['AUTH_MODE'] = os.environ.get('AUTH_MODE', 'banco')  # 'banco' ou 'ldap'

mail = Mail(app)

from models import db, Registro, Responsavel
db.init_app(app)
import users
from flask_login import UserMixin
from models import db
from models import User
from models import Configuracao

# Logger configurado para produção
logger = logging.getLogger(__name__)

# Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Inicializar Flask-Principal
principals = Principal(app)

# Permissões padrão sugeridas
PERMISSOES_PADRAO = {
    'admin': ['manage_access', 'manage_registros', 'manage_responsaveis', 'manage_config', 'send_alerts'],
    'gestor_acessos': ['manage_access'],
    'operador': ['manage_registros', 'manage_responsaveis', 'send_alerts'],
    'visualizador': []
}

# Carregar permissões do usuário logado
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    if hasattr(current_user, 'role') and current_user.role:
        identity.provides.add(RoleNeed(current_user.role.nome))
        # Adiciona permissões do perfil
        for perm in current_user.role.permissions:
            identity.provides.add(Need('permission', perm.nome))

# --- Decorators e RBAC ---

def permission_required(permission_name):
    """
    Decorator para proteger rotas por permissão.
    Exemplo: @permission_required('manage_access')
    Checa se o usuário logado tem a permissão via seu perfil (role).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Primeiro verifica se está logado
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            
            # Depois verifica a permissão
            need = Need('permission', permission_name)
            if not hasattr(g, 'identity') or need not in getattr(g.identity, 'provides', set()):
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Rotas principais ---

@app.route('/')
def index():
    """Redireciona a raiz para a tela de login."""
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Tela de login. Dispara identity_changed após login para RBAC funcionar corretamente."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        auth_mode = app.config.get('AUTH_MODE', 'banco')
        user = User.query.filter_by(username=username).first()
        # Admin sempre autentica pelo banco
        if user and user.username == 'admin':
            if user.status != 'ativo':
                flash('Usuário admin inativo ou bloqueado.', 'danger')
                return render_template('login.html')
            if user.password and check_password_hash(user.password, password):
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha inválidos', 'danger')
                return render_template('login.html')
        # Autenticação por banco
        if auth_mode == 'banco':
            if user and user.status == 'ativo' and user.password and check_password_hash(user.password, password):
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha inválidos', 'danger')
                return render_template('login.html')
        # Autenticação por LDAP
        elif auth_mode == 'ldap':
            # Exemplo de configuração LDAP (ajuste conforme seu AD)
            LDAP_SERVER = os.environ.get('LDAP_SERVER', 'ldap://seu-servidor-ldap')
            LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=empresa,dc=com,dc=br')
            LDAP_USER_DN = os.environ.get('LDAP_USER_DN', 'ou=usuarios')
            LDAP_USER_ATTR = os.environ.get('LDAP_USER_ATTR', 'sAMAccountName')
            try:
                server = Server(LDAP_SERVER, get_info=ALL)
                user_dn = f'{LDAP_USER_ATTR}={username},{LDAP_USER_DN},{LDAP_BASE_DN}'
                conn = Connection(server, user=user_dn, password=password, authentication=SIMPLE, auto_bind=True)
                # Se autenticar, busca ou cria usuário local
                if not user:
                    user = User(username=username, email=f'{username}@empresa.com.br', status='ativo', ldap_user=True)
                    db.session.add(user)
                    db.session.commit()
                if user.status != 'ativo':
                    flash('Usuário inativo ou bloqueado.', 'danger')
                    return render_template('login.html')
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash('Usuário ou senha inválidos (LDAP)', 'danger')
                return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout do usuário atual."""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Registro
    total_registros = Registro.query.count()
    vencidos = Registro.query.filter(Registro.data_vencimento < date.today(), Registro.regularizado == False).count()
    vencendo = Registro.query.filter(Registro.data_vencimento >= date.today(), Registro.data_vencimento <= (date.today() + timedelta(days=7)), Registro.regularizado == False).count()
    validos = total_registros - vencidos - vencendo
    
    # Contagem por tipo
    certificados = Registro.query.filter(Registro.tipo == 'certificado').count()
    senhas = Registro.query.filter(Registro.tipo == 'senha').count()
    licencas = Registro.query.filter(Registro.tipo == 'licenca').count()
    
    return render_template('dashboard.html', 
                         total_registros=total_registros, 
                         vencidos=vencidos, 
                         vencendo=vencendo,
                         validos=validos,
                         certificados=certificados,
                         senhas=senhas,
                         licencas=licencas)

@app.route('/dashboard-vencimentos')
@login_required
def dashboard_vencimentos():
    from models import Registro
    from datetime import date, timedelta
    
    hoje = date.today()
    
    # Próximos 7 dias (crítico)
    proximos_7_dias = Registro.query.filter(
        Registro.data_vencimento >= hoje,
        Registro.data_vencimento <= hoje + timedelta(days=7),
        Registro.regularizado == False
    ).order_by(Registro.data_vencimento).all()
    
    # Próximos 30 dias (atenção)
    proximos_30_dias = Registro.query.filter(
        Registro.data_vencimento > hoje + timedelta(days=7),
        Registro.data_vencimento <= hoje + timedelta(days=30),
        Registro.regularizado == False
    ).order_by(Registro.data_vencimento).all()
    
    # Vencidos há mais de 30 dias (urgente)
    vencidos_30_dias = Registro.query.filter(
        Registro.data_vencimento < hoje - timedelta(days=30),
        Registro.regularizado == False
    ).order_by(Registro.data_vencimento).all()
    
    # Dados para gráfico temporal (últimos 90 dias + próximos 30 dias)
    datas_grafico = []
    vencimentos_grafico = []
    
    for i in range(-90, 31):  # -90 dias até +30 dias
        data = hoje + timedelta(days=i)
        count = Registro.query.filter(
            Registro.data_vencimento == data,
            Registro.regularizado == False
        ).count()
        if count > 0:  # Só adiciona se há vencimentos
            datas_grafico.append(data.strftime('%d/%m'))
            vencimentos_grafico.append(count)
    
    return render_template('dashboard_vencimentos.html',
                         proximos_7_dias=proximos_7_dias,
                         proximos_30_dias=proximos_30_dias,
                         vencidos_30_dias=vencidos_30_dias,
                         datas_grafico=datas_grafico,
                         vencimentos_grafico=vencimentos_grafico,
                         hoje=hoje)

@app.route('/dashboard-responsaveis')
@login_required
def dashboard_responsaveis():
    from models import Registro, Responsavel
    from datetime import date
    
    hoje = date.today()
    
    # Buscar todos os responsáveis com contagem de itens
    responsaveis_stats = []
    todos_responsaveis = Responsavel.query.all()
    
    for responsavel in todos_responsaveis:
        # Total de itens
        total_itens = len(responsavel.registros)
        
        # Itens vencidos
        itens_vencidos = sum(1 for r in responsavel.registros 
                           if r.data_vencimento < hoje and not r.regularizado)
        
        # Itens em alerta (próximos 7 dias)
        itens_alerta = sum(1 for r in responsavel.registros 
                          if r.data_vencimento >= hoje and 
                          r.data_vencimento <= hoje + timedelta(days=7) and 
                          not r.regularizado)
        
        # Itens válidos
        itens_validos = total_itens - itens_vencidos - itens_alerta
        
        responsaveis_stats.append({
            'responsavel': responsavel,
            'total_itens': total_itens,
            'itens_vencidos': itens_vencidos,
            'itens_alerta': itens_alerta,
            'itens_validos': itens_validos
        })
    
    # Ordenar por total de itens (ranking)
    responsaveis_stats.sort(key=lambda x: x['total_itens'], reverse=True)
    
    # Top 5 responsáveis
    top_5 = responsaveis_stats[:5]
    
    # Responsáveis com itens vencidos
    responsaveis_com_vencidos = [r for r in responsaveis_stats if r['itens_vencidos'] > 0]
    
    # Dados para gráfico de pizza (top 10)
    top_10_nomes = [r['responsavel'].nome for r in responsaveis_stats[:10]]
    top_10_quantidades = [r['total_itens'] for r in responsaveis_stats[:10]]
    
    return render_template('dashboard_responsaveis.html',
                         responsaveis_stats=responsaveis_stats,
                         top_5=top_5,
                         responsaveis_com_vencidos=responsaveis_com_vencidos,
                         top_10_nomes=top_10_nomes,
                         top_10_quantidades=top_10_quantidades,
                         hoje=hoje)

@app.route('/dashboard-atividade')
@login_required
def dashboard_atividade():
    from models import Registro, User
    from datetime import date, datetime, timedelta
    
    hoje = date.today()
    
    # Últimos 10 registros criados
    ultimos_registros = Registro.query.order_by(Registro.id.desc()).limit(10).all()
    
    # Últimas 10 alterações (simulado - em um sistema real teríamos uma tabela de logs)
    # Por enquanto, vamos mostrar os registros mais recentemente modificados
    ultimas_alteracoes = Registro.query.order_by(Registro.id.desc()).limit(10).all()
    
    # Estatísticas dos últimos 30 dias
    registros_30_dias = Registro.query.filter(
        Registro.id >= 1  # Simulando registros recentes
    ).count()
    
    # Usuários mais ativos (simulado)
    usuarios_ativos = User.query.filter(User.status == 'ativo').count()
    
    # Dados para gráfico de atividade (últimos 7 dias)
    datas_atividade = []
    contagem_atividade = []
    
    for i in range(7, 0, -1):  # Últimos 7 dias
        data = hoje - timedelta(days=i)
        # Simulando atividade baseada no ID dos registros
        count = Registro.query.filter(Registro.id >= 1).count() // 7  # Distribuição simulada
        datas_atividade.append(data.strftime('%d/%m'))
        contagem_atividade.append(count)
    
    # Hoje
    count_hoje = Registro.query.filter(Registro.id >= 1).count() // 7
    datas_atividade.append(hoje.strftime('%d/%m'))
    contagem_atividade.append(count_hoje)
    
    return render_template('dashboard_atividade.html',
                         ultimos_registros=ultimos_registros,
                         ultimas_alteracoes=ultimas_alteracoes,
                         registros_30_dias=registros_30_dias,
                         usuarios_ativos=usuarios_ativos,
                         datas_atividade=datas_atividade,
                         contagem_atividade=contagem_atividade,
                         hoje=hoje)

@app.route('/registros')
@login_required
def listar_registros():
    sort = request.args.get('sort', 'data_vencimento')
    order = request.args.get('order', 'asc')
    busca_nome = request.args.get('busca_nome', '').strip()
    busca_tipo = request.args.get('busca_tipo', '').strip()
    busca_responsavel = request.args.get('busca_responsavel', '').strip()
    busca_status = request.args.get('busca_status', '').strip()
    valid_columns = {
        'nome': Registro.nome,
        'tipo': Registro.tipo,
        'data_vencimento': Registro.data_vencimento,
        'regularizado': Registro.regularizado
    }
    sort_col = valid_columns.get(sort, Registro.data_vencimento)
    query = Registro.query
    if busca_nome:
        query = query.filter(Registro.nome.ilike(f'%{busca_nome}%'))
    if busca_tipo:
        query = query.filter(Registro.tipo == busca_tipo)
    if busca_status == 'sim':
        query = query.filter(Registro.regularizado == True)
    elif busca_status == 'nao':
        query = query.filter(Registro.regularizado == False)
    if busca_responsavel:
        query = query.join(Registro.responsaveis).filter(Responsavel.nome.ilike(f'%{busca_responsavel}%'))
    if order == 'desc':
        registros = query.order_by(sort_col.desc()).all()
    else:
        registros = query.order_by(sort_col.asc()).all()
    from datetime import date
    return render_template('registros/list.html', registros=registros, hoje=date.today(), sort=sort, order=order)

@app.route('/registros/novo', methods=['GET', 'POST'])
@permission_required('manage_registros')
@login_required
def novo_registro():
    todos_responsaveis = Responsavel.query.order_by(Responsavel.nome).all()
    if request.method == 'POST':
        nome = request.form['nome']
        origem = request.form['origem']
        tipo = request.form['tipo']
        data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        tempo_alerta = int(request.form['tempo_alerta'])
        observacoes = request.form['observacoes']
        responsaveis_ids = request.form.getlist('responsaveis')
        responsaveis = Responsavel.query.filter(Responsavel.id.in_(responsaveis_ids)).all()
        dias_para_vencer = (data_vencimento - date.today()).days
        if dias_para_vencer <= tempo_alerta:
            regularizado = False
        else:
            regularizado = True
        registro = Registro(
            nome=nome,
            origem=origem,
            tipo=tipo,
            data_vencimento=data_vencimento,
            tempo_alerta=tempo_alerta,
            observacoes=observacoes,
            regularizado=regularizado,
            responsaveis=responsaveis
        )
        db.session.add(registro)
        db.session.commit()
        flash('Registro criado com sucesso!', 'success')
        return redirect(url_for('listar_registros'))
    return render_template('registros/form.html', registro=None, todos_responsaveis=todos_responsaveis)

@app.route('/registros/<int:registro_id>/editar', methods=['GET', 'POST'])
@permission_required('manage_registros')
@login_required
def editar_registro(registro_id):
    registro = Registro.query.get_or_404(registro_id)
    todos_responsaveis = Responsavel.query.order_by(Responsavel.nome).all()
    if request.method == 'POST':
        registro.nome = request.form['nome']
        registro.origem = request.form['origem']
        registro.tipo = request.form['tipo']
        registro.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        registro.tempo_alerta = int(request.form['tempo_alerta'])
        registro.observacoes = request.form['observacoes']
        responsaveis_ids = request.form.getlist('responsaveis')
        registro.responsaveis = Responsavel.query.filter(Responsavel.id.in_(responsaveis_ids)).all()
        dias_para_vencer = (registro.data_vencimento - date.today()).days
        if dias_para_vencer <= registro.tempo_alerta:
            registro.regularizado = False
        else:
            registro.regularizado = True
        db.session.commit()
        flash('Registro atualizado com sucesso!', 'success')
        return redirect(url_for('listar_registros'))
    return render_template('registros/form.html', registro=registro, todos_responsaveis=todos_responsaveis)

@app.route('/registros/<int:registro_id>/excluir', methods=['GET', 'POST'])
@permission_required('manage_registros')
@login_required
def excluir_registro(registro_id):
    registro = Registro.query.get_or_404(registro_id)
    if request.method == 'POST':
        db.session.delete(registro)
        db.session.commit()
        flash('Registro excluído com sucesso!', 'success')
        return redirect(url_for('listar_registros'))
    return render_template('registros/confirm_delete.html', registro=registro)

@app.route('/registros/<int:registro_id>/regularizar', methods=['POST'])
@permission_required('manage_registros')
@login_required
def regularizar_registro(registro_id):
    registro = Registro.query.get_or_404(registro_id)
    registro.regularizado = True
    db.session.commit()
    flash('Registro marcado como regularizado!', 'success')
    return redirect(url_for('listar_registros'))

@app.route('/responsaveis')
@login_required
def listar_responsaveis():
    responsaveis = Responsavel.query.order_by(Responsavel.nome).all()
    return render_template('responsaveis/list.html', responsaveis=responsaveis)

@app.route('/responsaveis/novo', methods=['GET', 'POST'])
@permission_required('manage_responsaveis')
@login_required
def novo_responsavel():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        responsavel = Responsavel(nome=nome, email=email)
        db.session.add(responsavel)
        db.session.commit()
        flash('Responsável criado com sucesso!', 'success')
        return redirect(url_for('listar_responsaveis'))
    return render_template('responsaveis/form.html', responsavel=None)

@app.route('/responsaveis/<int:responsavel_id>/editar', methods=['GET', 'POST'])
@permission_required('manage_responsaveis')
@login_required
def editar_responsavel(responsavel_id):
    responsavel = Responsavel.query.get_or_404(responsavel_id)
    if request.method == 'POST':
        responsavel.nome = request.form['nome']
        responsavel.email = request.form['email']
        db.session.commit()
        flash('Responsável atualizado com sucesso!', 'success')
        return redirect(url_for('listar_responsaveis'))
    return render_template('responsaveis/form.html', responsavel=responsavel)

@app.route('/responsaveis/<int:responsavel_id>/excluir', methods=['GET', 'POST'])
@permission_required('manage_responsaveis')
@login_required
def excluir_responsavel(responsavel_id):
    responsavel = Responsavel.query.get_or_404(responsavel_id)
    if request.method == 'POST':
        db.session.delete(responsavel)
        db.session.commit()
        flash('Responsável excluído com sucesso!', 'success')
        return redirect(url_for('listar_responsaveis'))
    return render_template('responsaveis/confirm_delete.html', responsavel=responsavel)

@app.route('/configuracao', methods=['GET', 'POST'])
@permission_required('manage_config')
@login_required
def configuracao():
    config = Configuracao.query.first()
    if not config:
        config = Configuracao(dia_semana='fri', hora=14, minuto=0)
        db.session.add(config)
        db.session.commit()
    
    # Carregar configurações LDAP do ambiente
    ldap_config = {
        'ldap_server': os.environ.get('LDAP_SERVER', 'ldap://seu-servidor-ldap'),
        'ldap_port': int(os.environ.get('LDAP_PORT', 389)),
        'ldap_base_dn': os.environ.get('LDAP_BASE_DN', 'dc=empresa,dc=com,dc=br'),
        'ldap_user_dn': os.environ.get('LDAP_USER_DN', 'ou=usuarios'),
        'ldap_user_attr': os.environ.get('LDAP_USER_ATTR', 'sAMAccountName'),
        'ldap_bind_dn': os.environ.get('LDAP_BIND_DN', ''),
        'ldap_bind_password': os.environ.get('LDAP_BIND_PASSWORD', ''),
        'ldap_email_attr': os.environ.get('LDAP_EMAIL_ATTR', 'mail')
    }
    
    # Carregar configurações de email
    email_config = {
        'mail_server': config.mail_server if config else 'smtp.gmail.com',
        'mail_port': config.mail_port if config else 587,
        'mail_username': config.mail_username if config else '',
        'mail_password': config.mail_password if config else '',
        'mail_use_tls': config.mail_use_tls if config else 'tls',
        'mail_default_sender': config.mail_default_sender if config else ''
    }
    
    if request.method == 'POST':
        # Verificar se agendamento está ativo antes de pegar os valores
        agendamento_ativo = 'agendamento_ativo' in request.form
        
        if agendamento_ativo:
            config.dia_semana = request.form.get('dia_semana', 'fri')
            config.hora = int(request.form.get('hora', 14))
            config.minuto = int(request.form.get('minuto', 0))
        else:
            # Manter valores atuais se agendamento estiver desativado
            pass
            
        config.agendamento_ativo = agendamento_ativo
        
        # Salvar configurações de email
        config.mail_server = request.form.get('mail_server', 'smtp.gmail.com')
        config.mail_port = int(request.form.get('mail_port', 587))
        config.mail_username = request.form.get('mail_username', '')
        config.mail_password = request.form.get('mail_password', '')
        config.mail_use_tls = request.form.get('mail_use_tls', 'tls')
        config.mail_default_sender = request.form.get('mail_default_sender', '')
        
        # Atualizar modo de autenticação
        auth_mode = request.form.get('auth_mode', 'banco')
        app.config['AUTH_MODE'] = auth_mode
        
        # Salvar configurações LDAP no ambiente (se for LDAP)
        if auth_mode == 'ldap':
            os.environ['LDAP_SERVER'] = request.form.get('ldap_server', 'ldap://seu-servidor-ldap')
            os.environ['LDAP_PORT'] = request.form.get('ldap_port', '389')
            os.environ['LDAP_BASE_DN'] = request.form.get('ldap_base_dn', 'dc=empresa,dc=com,dc=br')
            os.environ['LDAP_USER_DN'] = request.form.get('ldap_user_dn', 'ou=usuarios')
            os.environ['LDAP_USER_ATTR'] = request.form.get('ldap_user_attr', 'sAMAccountName')
            os.environ['LDAP_BIND_DN'] = request.form.get('ldap_bind_dn', '')
            os.environ['LDAP_BIND_PASSWORD'] = request.form.get('ldap_bind_password', '')
            os.environ['LDAP_EMAIL_ATTR'] = request.form.get('ldap_email_attr', 'mail')
        
        db.session.commit()
        
        # Recarregar agendamento se necessário
        if 'agendamento_ativo' in request.form:
            recarregar_agendamento()
        
        flash('Configuração atualizada com sucesso!', 'success')
        return redirect(url_for('configuracao'))
    
    return render_template('configuracao/form.html', 
                         config=config, 
                         auth_mode=app.config.get('AUTH_MODE', 'banco'),
                         ldap_config=ldap_config,
                         email_config=email_config)

@app.route('/testar-ldap', methods=['POST'])
@permission_required('manage_config')
@login_required
def testar_ldap():
    """Testa a conexão LDAP com as configurações fornecidas."""
    try:
        from ldap3 import Server, Connection, ALL, SIMPLE
        
        # Pegar configurações do formulário
        ldap_server = request.form.get('ldap_server', 'ldap://localhost')
        ldap_port = int(request.form.get('ldap_port', 389))
        ldap_base_dn = request.form.get('ldap_base_dn', 'dc=empresa,dc=com,dc=br')
        ldap_user_dn = request.form.get('ldap_user_dn', 'ou=usuarios')
        ldap_user_attr = request.form.get('ldap_user_attr', 'sAMAccountName')
        ldap_bind_dn = request.form.get('ldap_bind_dn', '')
        ldap_bind_password = request.form.get('ldap_bind_password', '')
        
        # Construir URL do servidor
        if ldap_server.startswith('ldap://') or ldap_server.startswith('ldaps://'):
            server_url = f"{ldap_server}:{ldap_port}"
        else:
            server_url = f"ldap://{ldap_server}:{ldap_port}"
        
        # Criar servidor
        server = Server(server_url, get_info=ALL)
        
        # Tentar conexão
        if ldap_bind_dn and ldap_bind_password:
            # Bind com credenciais específicas
            conn = Connection(server, user=ldap_bind_dn, password=ldap_bind_password, authentication=SIMPLE, auto_bind=True)
        else:
            # Bind anônimo
            conn = Connection(server, auto_bind=True)
        
        if conn.bound:
            # Testar busca básica
            search_base = f"{ldap_user_dn},{ldap_base_dn}"
            conn.search(search_base, f"({ldap_user_attr}=*)", attributes=[ldap_user_attr])
            
            return jsonify({
                'success': True,
                'message': f'Conexão LDAP bem-sucedida! Encontrados {len(conn.entries)} usuários.',
                'users_found': len(conn.entries)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha na conexão LDAP: Não foi possível fazer bind.'
            })
            
    except Exception as e:
        logger.error(f"Erro ao testar LDAP: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro na conexão LDAP: {str(e)}'
        })

@app.route('/testar-email', methods=['POST'])
@permission_required('manage_config')
@login_required
def testar_email():
    """Testa a configuração de email com as configurações fornecidas."""
    try:
        from flask_mail import Mail, Message
        
        # Pegar configurações do formulário
        mail_server = request.form.get('mail_server', 'smtp.gmail.com')
        mail_port = int(request.form.get('mail_port', 587))
        mail_username = request.form.get('mail_username', '')
        mail_password = request.form.get('mail_password', '')
        mail_use_tls = request.form.get('mail_use_tls', 'tls')
        mail_default_sender = request.form.get('mail_default_sender', '')
        
        if not mail_username or not mail_password:
            return jsonify({
                'success': False,
                'message': 'Usuário e senha são obrigatórios para teste de email.'
            })
        
        # Configurar Flask-Mail temporariamente
        test_app = app
        test_app.config['MAIL_SERVER'] = mail_server
        test_app.config['MAIL_PORT'] = mail_port
        test_app.config['MAIL_USE_TLS'] = mail_use_tls == 'tls'
        test_app.config['MAIL_USE_SSL'] = mail_use_tls == 'ssl'
        test_app.config['MAIL_USERNAME'] = mail_username
        test_app.config['MAIL_PASSWORD'] = mail_password
        test_app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender or mail_username
        
        test_mail = Mail(test_app)
        
        # Tentar enviar email de teste
        with test_app.app_context():
            msg = Message(
                subject='Teste de Configuração - Painel de Certificados',
                recipients=[mail_username],
                body=f'''Olá!

Este é um email de teste para verificar se a configuração SMTP está funcionando corretamente.

Configurações testadas:
- Servidor: {mail_server}
- Porta: {mail_port}
- Segurança: {mail_use_tls.upper()}
- Usuário: {mail_username}

Se você recebeu este email, a configuração está funcionando perfeitamente!

Sistema de Certificados
'''
            )
            test_mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'Email de teste enviado com sucesso para {mail_username}!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao testar email: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro na configuração de email: {str(e)}'
        })

@app.route('/enviar-alertas')
@permission_required('send_alerts')
@login_required
def enviar_alertas_manual():
    """Envia alertas manualmente."""
    try:
        enviar_alertas_vencimento()
        flash('Alertas enviados com sucesso!', 'success')
        logger.info("Alertas enviados manualmente com sucesso")
    except Exception as e:
        logger.error(f"Erro ao enviar alertas: {e}")
        flash('Erro ao enviar alertas.', 'danger')
    return redirect(url_for('dashboard'))

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Salvar referência no app para uso posterior
    app.scheduler = scheduler
    
    # Carregar configuração do banco
    config = Configuracao.query.first()
    if config and config.agendamento_ativo:
        scheduler.add_job(
            func=lambda: enviar_alertas_vencimento(),
            trigger='cron',
            day_of_week=config.dia_semana,
            hour=config.hora,
            minute=config.minuto,
            id='envio_alertas_semanal',
            replace_existing=True
        )
        logger.info(f'Agendamento de alertas ativado: {config.dia_semana} às {config.hora}:{config.minuto}')
    else:
        if config:
            logger.info('Agendamento de alertas desativado pela configuração')
        else:
            logger.warning('Nenhuma configuração de alerta encontrada. O envio será desativado.')
    scheduler.start()

def recarregar_agendamento():
    """Recarrega o agendamento baseado na configuração atual."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        # Remover job existente se houver
        if hasattr(app, 'scheduler'):
            try:
                app.scheduler.remove_job('envio_alertas_semanal')
            except:
                pass  # Job não existe, ignorar
        
        # Carregar configuração atual
        config = Configuracao.query.first()
        if config and config.agendamento_ativo:
            # Adicionar novo job
            app.scheduler.add_job(
                func=lambda: enviar_alertas_vencimento(),
                trigger=CronTrigger(
                    day_of_week=config.dia_semana,
                    hour=config.hora,
                    minute=config.minuto
                ),
                id='envio_alertas_semanal',
                replace_existing=True
            )
            logger.info(f'Agendamento recarregado: {config.dia_semana} às {config.hora}:{config.minuto}')
        else:
            logger.info('Agendamento desativado via configuração')
            
    except Exception as e:
        logger.error(f'Erro ao recarregar agendamento: {e}')

if __name__ == '__main__':
    from app import app, db
    with app.app_context():
        db.create_all()
        start_scheduler()
    app.run(debug=True)

def enviar_email_responsaveis(registro):
    """Envia e-mail para todos os responsáveis de um registro."""
    dias_para_vencer = (registro.data_vencimento - date.today()).days
    
    # Verificar se o mail está configurado corretamente
    if app.config['MAIL_SERVER'] == 'localhost' and app.config['MAIL_PORT'] == 8025 and app.config['MAIL_SUPPRESS_SEND']:
        logger.info("Modo desenvolvimento: emails serão simulados")
        for resp in registro.responsaveis:
            if resp.email:
                logger.info(f"Email simulado enviado para {resp.email} sobre {registro.nome}")
            else:
                logger.warning(f"Responsável sem e-mail: {resp}")
        return
    
    for resp in registro.responsaveis:
        nome = resp.nome
        email = resp.email
        if email:
            try:
                msg = Message(
                    subject=f"[Alerta] {registro.tipo.title()} '{registro.nome}' vence em {dias_para_vencer} dias",
                    recipients=[email],
                    body=f"Olá {nome},\n\nO {registro.tipo} '{registro.nome}' vence em {dias_para_vencer} dias (Data de vencimento: {registro.data_vencimento}).\n\nObservações: {registro.observacoes or '-'}\n\nPor favor, regularize o quanto antes.\n\nSistema de Certificados"
                )
                mail.send(msg)
                logger.info(f"Alerta enviado para {email} sobre {registro.nome}")
            except Exception as e:
                logger.error(f"Erro ao enviar e-mail para {email}: {e}")
        else:
            logger.warning(f"Responsável sem e-mail: {resp}")

def enviar_alertas_vencimento():
    """Envia alertas de vencimento para todos os registros em período de alerta."""
    hoje = date.today()
    registros = Registro.query.filter_by(regularizado=False).all()
    logger.info(f"Iniciando verificação de alertas: {len(registros)} registros encontrados")
    
    for registro in registros:
        dias_para_vencer = (registro.data_vencimento - hoje).days
        if dias_para_vencer <= registro.tempo_alerta:
            logger.info(f"Enviando alerta para {registro.nome} (vence em {dias_para_vencer} dias)")
            enviar_email_responsaveis(registro)
        else:
            logger.debug(f"Registro {registro.nome} não está no período de alerta ({dias_para_vencer} dias > {registro.tempo_alerta})") 

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def novo_usuario():
    """Cadastro manual de usuário. Permite atribuir perfil (role)."""
    roles = Role.query.all()
    if request.method == 'POST':
        username = request.form['username']
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form.get('role_id')
        # Validação simples
        if not username or not nome or not email or not password or not role_id:
            flash('Usuário, nome, e-mail, senha e perfil são obrigatórios.', 'danger')
            return render_template('usuarios/form.html', roles=roles)
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'danger')
            return render_template('usuarios/form.html', roles=roles)
        from werkzeug.security import generate_password_hash
        user = User(username=username, nome=nome, email=email, password=generate_password_hash(password), role_id=int(role_id), status='ativo')
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/form.html', roles=roles)

@app.route('/usuarios')
@permission_required('manage_access')
@login_required
def listar_usuarios():
    """Listagem de usuários. Protegida por manage_access."""
    busca_login = request.args.get('busca_login', '').strip()
    busca_nome = request.args.get('busca_nome', '').strip()
    query = User.query
    if busca_login:
        query = query.filter(User.username.ilike(f'%{busca_login}%'))
    if busca_nome:
        query = query.filter(User.nome.ilike(f'%{busca_nome}%'))
    usuarios = query.all()
    return render_template('usuarios/list.html', usuarios=usuarios) 

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def editar_usuario(usuario_id):
    """Edição de usuário. Protege o admin para sempre ter o perfil admin e não permitir troca de perfil."""
    usuario = User.query.get_or_404(usuario_id)
    roles = Role.query.all()
    if request.method == 'POST':
        username = request.form['username']
        nome = request.form['nome']
        email = request.form['email']
        password = request.form['password']
        role_id = request.form.get('role_id')
        if not username or not nome or not email:
            flash('Usuário, nome e e-mail são obrigatórios.', 'danger')
            return render_template('usuarios/form.html', usuario=usuario, roles=roles)
        if User.query.filter(User.username == username, User.id != usuario.id).first():
            flash('Nome de usuário já existe.', 'danger')
            return render_template('usuarios/form.html', usuario=usuario, roles=roles)
        usuario.username = username
        usuario.nome = nome
        usuario.email = email
        if password:
            from werkzeug.security import generate_password_hash
            usuario.password = generate_password_hash(password)
        # Proteção: admin sempre com perfil admin
        if usuario.username == 'admin':
            admin_role = Role.query.filter_by(nome='admin').first()
            usuario.role_id = admin_role.id
        elif role_id:
            usuario.role_id = int(role_id)
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/form.html', usuario=usuario, roles=roles)

@app.route('/usuarios/<int:usuario_id>/excluir', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def excluir_usuario(usuario_id):
    """Exclusão de usuário. Protegida por manage_access."""
    usuario = User.query.get_or_404(usuario_id)
    if request.method == 'POST':
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário excluído com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/confirm_delete.html', usuario=usuario) 

@app.route('/usuarios/<int:usuario_id>/resetar-senha', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def resetar_senha_usuario(usuario_id):
    usuario = User.query.get_or_404(usuario_id)
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        if not nova_senha:
            flash('A nova senha é obrigatória.', 'danger')
            return render_template('usuarios/resetar_senha.html', usuario=usuario)
        from werkzeug.security import generate_password_hash
        usuario.password = generate_password_hash(nova_senha)
        db.session.commit()
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuarios/resetar_senha.html', usuario=usuario) 

@app.route('/perfis')
@permission_required('manage_access')
@login_required
def listar_perfis():
    """Listagem de perfis (roles). Protegida por manage_access."""
    perfis = Role.query.all()
    return render_template('perfis/list.html', perfis=perfis) 

@app.route('/perfis/novo', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def novo_perfil():
    """Cadastro de novo perfil (role) com seleção de permissões."""
    permissoes = Permission.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        perms_ids = request.form.getlist('permissoes')
        if not nome:
            flash('Nome do perfil é obrigatório.', 'danger')
            return render_template('perfis/form.html', permissoes=permissoes)
        if Role.query.filter_by(nome=nome).first():
            flash('Já existe um perfil com esse nome.', 'danger')
            return render_template('perfis/form.html', permissoes=permissoes)
        perfil = Role(nome=nome, descricao=descricao)
        for pid in perms_ids:
            perm = Permission.query.get(int(pid))
            if perm:
                perfil.permissions.append(perm)
        db.session.add(perfil)
        db.session.commit()
        flash('Perfil criado com sucesso!', 'success')
        return redirect(url_for('listar_perfis'))
    return render_template('perfis/form.html', permissoes=permissoes) 

@app.route('/perfis/<int:perfil_id>/editar', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def editar_perfil(perfil_id):
    """Edição de perfil (role). Permite alterar nome, descrição e permissões."""
    perfil = Role.query.get_or_404(perfil_id)
    permissoes = Permission.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        perms_ids = request.form.getlist('permissoes')
        if not nome:
            flash('Nome do perfil é obrigatório.', 'danger')
            return render_template('perfis/form.html', perfil=perfil, permissoes=permissoes)
        if Role.query.filter(Role.nome == nome, Role.id != perfil.id).first():
            flash('Já existe um perfil com esse nome.', 'danger')
            return render_template('perfis/form.html', perfil=perfil, permissoes=permissoes)
        perfil.nome = nome
        perfil.descricao = descricao
        perfil.permissions = [Permission.query.get(int(pid)) for pid in perms_ids]
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('listar_perfis'))
    return render_template('perfis/form.html', perfil=perfil, permissoes=permissoes) 

@app.route('/perfis/<int:perfil_id>/excluir', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def excluir_perfil(perfil_id):
    """Exclusão de perfil. Não permite excluir admin nem perfis em uso."""
    perfil = Role.query.get_or_404(perfil_id)
    if perfil.nome == 'admin':
        flash('O perfil admin não pode ser excluído.', 'danger')
        return redirect(url_for('listar_perfis'))
    if perfil.users:
        flash('Não é possível excluir um perfil associado a usuários.', 'danger')
        return redirect(url_for('listar_perfis'))
    if request.method == 'POST':
        db.session.delete(perfil)
        db.session.commit()
        flash('Perfil excluído com sucesso!', 'success')
        return redirect(url_for('listar_perfis'))
    return render_template('perfis/confirm_delete.html', perfil=perfil) 