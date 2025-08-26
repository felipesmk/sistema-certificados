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
from models import Role, Permission, RoleHistory, RoleTemplate, UserHistory

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

from utils.cache import cached

@cached(ttl_seconds=300)  # Cache por 5 minutos
def get_system_config():
    """Obtém as configurações do sistema para uso global."""
    try:
        with app.app_context():
            config = Configuracao.query.first()
            if not config:
                # Criar configuração padrão se não existir
                config = Configuracao()
                db.session.add(config)
                db.session.commit()
            
            # Fazer uma cópia dos dados para evitar problemas de sessão
            config_data = {
                'id': config.id,
                'dia_semana': config.dia_semana,
                'hora': config.hora,
                'minuto': config.minuto,
                'agendamento_ativo': config.agendamento_ativo,
                'mail_server': config.mail_server,
                'mail_port': config.mail_port,
                'mail_username': config.mail_username,
                'mail_password': config.mail_password,
                'mail_use_tls': config.mail_use_tls,
                'mail_default_sender': config.mail_default_sender,
                'nome_sistema': config.nome_sistema,
                'equipe_ti': config.equipe_ti,
                'email_ti': config.email_ti,
                'telefone_ti': config.telefone_ti,
                'logo_url': config.logo_url,
            }
            return type('Configuracao', (), config_data)()
    except Exception as e:
        logger.error(f"Erro ao obter configurações do sistema: {e}")
        # Retornar configurações padrão em caso de erro
        return type('Configuracao', (), {
            'nome_sistema': 'Sistema de Certificados',
            'equipe_ti': 'Equipe de TI',
            'email_ti': 'ti@empresa.com',
            'telefone_ti': '(11) 99999-9999',
            
        })()

# Context processor para disponibilizar configurações em todos os templates
@app.context_processor
def inject_system_config():
    """Injeta as configurações do sistema em todos os templates."""
    try:
        return {
            'system_config': get_system_config()
        }
    except Exception as e:
        logger.error(f"Erro no context processor: {e}")
        # Retornar configurações padrão em caso de erro
        return {
            'system_config': type('Configuracao', (), {
                'nome_sistema': 'Sistema de Certificados',
                'equipe_ti': 'Equipe de TI',
                'email_ti': 'ti@empresa.com',
                'telefone_ti': '(11) 99999-9999',
            })()
        }

# Filtro personalizado para converter JSON string em dicionário
@app.template_filter('from_json')
def from_json_filter(value):
    """Converte string JSON em dicionário Python."""
    if not value or not isinstance(value, str):
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

# Filtro personalizado para valor absoluto
@app.template_filter('abs')
def abs_filter(value):
    """Retorna o valor absoluto de um número."""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value

# Configurações do Flask com suporte a variáveis de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://certificados_user:certificados123@localhost:5432/certificados_db')
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

from models import db, Registro, Responsavel, User, Configuracao
db.init_app(app)
from flask_login import UserMixin

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
            if user.status == 'bloqueado':
                flash('Usuário admin está bloqueado.', 'danger')
                return render_template('login.html')
            if user.status != 'ativo':
                flash('Usuário admin inativo.', 'danger')
                return render_template('login.html')
            if user.password and check_password_hash(user.password, password):
                # Atualiza login info
                from datetime import datetime
                user.last_login = datetime.now()
                user.login_count = (user.login_count or 0) + 1
                db.session.commit()
                historico = UserHistory(
                    user_id=user.id,
                    acao='login',
                    detalhes=None,
                    usuario=user.username,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:255]
                )
                db.session.add(historico)
                db.session.commit()
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
            else:
                flash('Usuário ou senha inválidos', 'danger')
                return render_template('login.html')
        # Autenticação por banco
        if auth_mode == 'banco':
            if user:
                if user.status == 'bloqueado':
                    flash('Usuário bloqueado. Contate o administrador.', 'danger')
                    return render_template('login.html')
                if user.status != 'ativo':
                    flash('Usuário inativo.', 'danger')
                    return render_template('login.html')
                if user.password and check_password_hash(user.password, password):
                    from datetime import datetime
                    user.last_login = datetime.now()
                    user.login_count = (user.login_count or 0) + 1
                    db.session.commit()
                    historico = UserHistory(
                        user_id=user.id,
                        acao='login',
                        detalhes=None,
                        usuario=user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    db.session.commit()
                login_user(user)
                identity_changed.send(app, identity=Identity(user.id))
                return redirect(url_for('dashboard'))
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
                if user.status == 'bloqueado':
                    flash('Usuário bloqueado. Contate o administrador.', 'danger')
                    return render_template('login.html')
                if user.status != 'ativo':
                    flash('Usuário inativo.', 'danger')
                    return render_template('login.html')
                from datetime import datetime
                user.last_login = datetime.now()
                user.login_count = (user.login_count or 0) + 1
                db.session.commit()
                historico = UserHistory(
                    user_id=user.id,
                    acao='login',
                    detalhes=None,
                    usuario=user.username,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:255]
                )
                db.session.add(historico)
                db.session.commit()
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
        
        # Salvar configurações de personalização (simplificadas)
        config.nome_sistema = request.form.get('nome_sistema', 'Sistema de Certificados')
        config.equipe_ti = request.form.get('equipe_ti', 'Equipe de TI')
        config.email_ti = request.form.get('email_ti', 'ti@empresa.com')
        config.telefone_ti = request.form.get('telefone_ti', '(11) 99999-9999')
        config.logo_url = request.form.get('logo_url', '')

        
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
    
    # Retorno para método GET
    return render_template('configuracao/form_colapsavel.html', 
                          config=config, 
                          auth_mode=app.config.get('AUTH_MODE', 'banco'),
                          ldap_config=ldap_config,
                          email_config=email_config)

@app.route('/configuracao/salvar-secao/<secao>', methods=['POST'])
@permission_required('manage_config')
@login_required
def salvar_secao_configuracao(secao):
    """Salva uma seção específica da configuração."""
    try:
        config = Configuracao.query.first()
        if not config:
            config = Configuracao()
            db.session.add(config)
        
        if secao == 'auth':
            # Salvar configurações de autenticação
            auth_mode = request.form.get('auth_mode', 'banco')
            app.config['AUTH_MODE'] = auth_mode
            
            # Salvar configurações LDAP se for LDAP
            if auth_mode == 'ldap':
                os.environ['LDAP_SERVER'] = request.form.get('ldap_server', 'ldap://seu-servidor-ldap')
                os.environ['LDAP_PORT'] = request.form.get('ldap_port', '389')
                os.environ['LDAP_BASE_DN'] = request.form.get('ldap_base_dn', 'dc=empresa,dc=com,dc=br')
                os.environ['LDAP_USER_DN'] = request.form.get('ldap_user_dn', 'ou=usuarios')
                os.environ['LDAP_USER_ATTR'] = request.form.get('ldap_user_attr', 'sAMAccountName')
                os.environ['LDAP_BIND_DN'] = request.form.get('ldap_bind_dn', '')
                os.environ['LDAP_BIND_PASSWORD'] = request.form.get('ldap_bind_password', '')
                os.environ['LDAP_EMAIL_ATTR'] = request.form.get('ldap_email_attr', 'mail')
            
            mensagem = 'Configurações de autenticação salvas com sucesso!'
            
        elif secao == 'email':
            # Salvar configurações de email
            config.mail_server = request.form.get('mail_server', 'smtp.gmail.com')
            config.mail_port = int(request.form.get('mail_port', 587))
            config.mail_username = request.form.get('mail_username', '')
            config.mail_password = request.form.get('mail_password', '')
            config.mail_use_tls = request.form.get('mail_use_tls', 'tls')
            config.mail_default_sender = request.form.get('mail_default_sender', '')
            
            mensagem = 'Configurações de email salvas com sucesso!'
            
        elif secao == 'agendamento':
            # Salvar configurações de agendamento
            agendamento_ativo = 'agendamento_ativo' in request.form
            config.agendamento_ativo = agendamento_ativo
            
            if agendamento_ativo:
                config.dia_semana = request.form.get('dia_semana', 'fri')
                config.hora = int(request.form.get('hora', 14))
                config.minuto = int(request.form.get('minuto', 0))
                recarregar_agendamento()
            
            mensagem = 'Configurações de agendamento salvas com sucesso!'
            
        elif secao == 'personalizacao':
            # Salvar configurações de personalização (simplificadas)
            config.nome_sistema = request.form.get('nome_sistema', 'Sistema de Certificados')
            config.equipe_ti = request.form.get('equipe_ti', 'Equipe de TI')
            config.email_ti = request.form.get('email_ti', 'ti@empresa.com')
            config.telefone_ti = request.form.get('telefone_ti', '(11) 99999-9999')
            config.logo_url = request.form.get('logo_url', '')

            
            mensagem = 'Configurações de personalização salvas com sucesso!'
        
        else:
            return jsonify({'success': False, 'message': 'Seção inválida'}), 400
        
        db.session.commit()
        return jsonify({'success': True, 'message': mensagem})
        
    except Exception as e:
        logger.error(f"Erro ao salvar seção {secao}: {e}")
        return jsonify({'success': False, 'message': f'Erro ao salvar: {str(e)}'}), 500

@app.route('/testar-ldap', methods=['POST'])
@permission_required('manage_config')
@login_required
def testar_ldap():
    """Testa a conexão LDAP com as configurações fornecidas usando as funções melhoradas."""
    try:
        # Temporariamente definir variáveis de ambiente com os valores do formulário
        original_env = {}
        form_config = {
            'LDAP_SERVER': request.form.get('ldap_server', 'ldap://localhost'),
            'LDAP_PORT': request.form.get('ldap_port', '389'),
            'LDAP_BASE_DN': request.form.get('ldap_base_dn', 'dc=empresa,dc=com'),
            'LDAP_USER_DN': request.form.get('ldap_user_dn', 'ou=usuarios'),
            'LDAP_USER_ATTR': request.form.get('ldap_user_attr', 'sAMAccountName'),
            'LDAP_BIND_DN': request.form.get('ldap_bind_dn', ''),
            'LDAP_BIND_PASSWORD': request.form.get('ldap_bind_password', ''),
            'LDAP_EMAIL_ATTR': request.form.get('ldap_email_attr', 'mail'),
            'LDAP_NAME_ATTR': 'displayName',
            'LDAP_GROUP_ATTR': 'memberOf',
            'LDAP_TIMEOUT': '10'
        }
        
        # Salvar configurações originais e aplicar temporárias
        for key, value in form_config.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        # Limpar cache das configurações para usar as novas
        from routes.auth import get_ldap_server_config
        get_ldap_server_config.cache_clear()
        
        # Importar funções melhoradas
        from routes.auth import get_cached_ldap_connection, get_ldap_user_details
        
        # Testar conexão usando as funções melhoradas
        conn = get_cached_ldap_connection()
        
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Falha ao estabelecer conexão LDAP. Verifique servidor, porta e credenciais.'
            })
        
        # Testar busca de usuários
        config = get_ldap_server_config()
        search_base = f"{config['user_dn']},{config['base_dn']}"
        search_filter = f"({config['user_attr']}=*)"
        
        success = conn.search(search_base, search_filter, attributes=[config['user_attr']], size_limit=5)
        
        if success and conn.entries:
            # Testar busca de detalhes de um usuário específico
            first_user = str(conn.entries[0][config['user_attr']].value)
            user_details = get_ldap_user_details(first_user)
            
            result_msg = f"✅ Conexão LDAP bem-sucedida!\\n"
            result_msg += f"📊 Encontrados {len(conn.entries)} usuários (mostrando primeiros 5)\\n"
            result_msg += f"👤 Teste de detalhes do usuário '{first_user}': "
            
            if user_details:
                result_msg += f"✅ Sucesso\\n"
                result_msg += f"   📧 Email: {user_details.get('email', 'N/A')}\\n"
                result_msg += f"   👥 Grupos: {len(user_details.get('grupos', []))} encontrados"
            else:
                result_msg += "⚠️ Detalhes não obtidos"
            
            return jsonify({
                'success': True, 
                'message': result_msg
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Conexão estabelecida, mas nenhum usuário encontrado. Verifique User DN e Base DN.'
            })
            
    except Exception as e:
        logger.error(f"Erro ao testar LDAP melhorado: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro ao testar LDAP: {str(e)}'
        })
    finally:
        # Restaurar configurações originais
        for key, original_value in original_env.items():
            if original_value is not None:
                os.environ[key] = original_value
            elif key in os.environ:
                del os.environ[key]
        
        # Limpar cache novamente para usar configurações originais
        try:
            from routes.auth import get_ldap_server_config
            get_ldap_server_config.cache_clear()
        except:
            pass

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
            # Renderizar template HTML
            html_content = render_template('emails/email_teste.html',
                                         config={
                                             'mail_server': mail_server,
                                             'mail_port': mail_port,
                                             'mail_username': mail_username,
                                             'mail_use_tls': mail_use_tls,
                                             'mail_default_sender': mail_default_sender or mail_username
                                         },
                                         momento_teste=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                                         destinatario=mail_username,
                                         system_config=get_system_config(),
                                         subject='Teste de Configuração - Sistema de Certificados')
            
            msg = Message(
                subject='Teste de Configuração - Sistema de Certificados',
                recipients=[mail_username],
                html=html_content,
                sender=mail_default_sender or mail_username
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

@app.route('/enviar-resumos')
@permission_required('send_alerts')
@login_required
def enviar_resumos_manual():
    """Envia emails de resumo para responsáveis manualmente."""
    try:
        emails_enviados = enviar_email_resumo_responsaveis()
        flash(f'Resumos enviados com sucesso! ({emails_enviados} emails)', 'success')
        logger.info(f"Resumos enviados manualmente: {emails_enviados} emails")
    except Exception as e:
        logger.error(f"Erro ao enviar resumos: {e}")
        flash('Erro ao enviar resumos.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/enviar-resumo-responsavel/<int:responsavel_id>')
@permission_required('send_alerts')
@login_required
def enviar_resumo_individual(responsavel_id):
    """Envia email de resumo para um responsável específico."""
    try:
        responsavel = Responsavel.query.get_or_404(responsavel_id)
        
        if not responsavel.email:
            flash('Este responsável não possui email cadastrado.', 'warning')
            return redirect(url_for('listar_responsaveis'))
        
        # Buscar certificados deste responsável (relação N:N)
        certificados = Registro.query.filter(Registro.responsaveis.contains(responsavel)).all()
        
        if not certificados:
            flash(f'O responsável {responsavel.nome} não possui certificados cadastrados.', 'info')
            return redirect(url_for('listar_responsaveis'))
        
        # Renderizar template HTML
        html_content = render_template('emails/email_responsaveis.html',
                                     responsavel=responsavel,
                                     certificados=certificados,
                                     hoje=date.today(),
                                     timedelta=timedelta,
                                     system_config=get_system_config(),
                                     subject=f"Resumo de Certificados - {responsavel.nome}")
        
        msg = Message(
            subject=f"Resumo de Certificados - {responsavel.nome}",
            recipients=[responsavel.email],
            html=html_content,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        flash(f'Resumo enviado com sucesso para {responsavel.nome} ({responsavel.email})!', 'success')
        logger.info(f"Resumo individual enviado para {responsavel.email}")
        
    except Exception as e:
        logger.error(f"Erro ao enviar resumo individual: {e}")
        flash(f'Erro ao enviar resumo: {str(e)}', 'danger')
    
    return redirect(url_for('listar_responsaveis'))

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
                # Renderizar template HTML
                html_content = render_template('emails/alerta_vencimento.html',
                                             registro=registro,
                                             dias_restantes=dias_para_vencer,
                                             system_config=get_system_config(),
                                             subject=f"Alerta de Vencimento - {registro.nome}")
                
                msg = Message(
                    subject=f"[Alerta] {registro.tipo.title()} '{registro.nome}' vence em {dias_para_vencer} dias",
                    recipients=[email],
                    html=html_content,
                    sender=app.config['MAIL_DEFAULT_SENDER']
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

def enviar_email_resumo_responsaveis():
    """Envia email de resumo para todos os responsáveis com seus certificados."""
    try:
        hoje = date.today()
        
        # Buscar todos os responsáveis que têm certificados
        responsaveis = Responsavel.query.join(Registro).distinct().all()
        
        emails_enviados = 0
        
        for responsavel in responsaveis:
            if not responsavel.email:
                continue
                
            # Buscar certificados deste responsável (relação N:N)
            certificados = Registro.query.filter(Registro.responsaveis.contains(responsavel)).all()
            
            if not certificados:
                continue
            
            try:
                # Renderizar template HTML
                html_content = render_template('emails/email_responsaveis.html',
                                             responsavel=responsavel,
                                             certificados=certificados,
                                             hoje=hoje,
                                             timedelta=timedelta,
                                             system_config=get_system_config(),
                                             subject=f"Resumo de Certificados - {responsavel.nome}")
                
                msg = Message(
                    subject=f"Resumo de Certificados - {responsavel.nome}",
                    recipients=[responsavel.email],
                    html=html_content,
                    sender=app.config['MAIL_DEFAULT_SENDER']
                )
                
                mail.send(msg)
                emails_enviados += 1
                logger.info(f"Email de resumo enviado para {responsavel.email}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar email de resumo para {responsavel.email}: {str(e)}")
        
        logger.info(f"Enviados {emails_enviados} emails de resumo")
        return emails_enviados
        
    except Exception as e:
        logger.error(f"Erro ao enviar emails de resumo: {str(e)}")
        return 0 

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def novo_usuario():
    """Cadastro manual de usuário com campos avançados."""
    import json
    from werkzeug.security import generate_password_hash
    
    roles = Role.query.filter_by(ativo=True).all()
    
    if request.method == 'POST':
        # Campos obrigatórios
        username = request.form.get('username', '').strip()
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role_id = request.form.get('role_id')
        
        # Campos opcionais
        telefone = request.form.get('telefone', '').strip()
        departamento = request.form.get('departamento', '').strip()
        cargo = request.form.get('cargo', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        status = request.form.get('status', 'ativo')
        
        # Validações
        erros = []
        
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        elif User.query.filter_by(username=username).first():
            erros.append('Nome de usuário já existe.')
        elif len(username) < 3:
            erros.append('Nome de usuário deve ter pelo menos 3 caracteres.')
            
        if not nome:
            erros.append('Nome completo é obrigatório.')
        elif len(nome) < 2:
            erros.append('Nome deve ter pelo menos 2 caracteres.')
            
        if not email:
            erros.append('E-mail é obrigatório.')
        elif User.query.filter_by(email=email).first():
            erros.append('E-mail já está em uso.')
        elif '@' not in email or '.' not in email:
            erros.append('E-mail deve ter formato válido.')
            
        if not password:
            erros.append('Senha é obrigatória.')
        elif len(password) < 6:
            erros.append('Senha deve ter pelo menos 6 caracteres.')
            
        if not role_id:
            erros.append('Perfil é obrigatório.')
        elif not Role.query.get(role_id):
            erros.append('Perfil selecionado não existe.')
            
        if telefone and len(telefone) < 8:
            erros.append('Telefone deve ter pelo menos 8 dígitos.')
            
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('usuarios/form.html', 
                                 roles=roles,
                                 form_data=request.form)
        
        try:
            # Criar usuário
            user = User(
                username=username,
                nome=nome,
                email=email,
                password=generate_password_hash(password),
                role_id=int(role_id),
                status=status,
                telefone=telefone or None,
                departamento=departamento or None,
                cargo=cargo or None,
                observacoes=observacoes or None,
                created_by=current_user.username
            )
            
            db.session.add(user)
            db.session.flush()  # Para obter o ID
            
            # Registrar histórico
            historico = UserHistory(
                user_id=user.id,
                acao='created',
                detalhes=json.dumps({
                    'created_by': current_user.username,
                    'initial_role': Role.query.get(role_id).nome,
                    'status': status
                }),
                usuario=current_user.username,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            db.session.add(historico)
            
            db.session.commit()
            
            flash(f'Usuário "{username}" criado com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar usuário: {str(e)}', 'danger')
            app.logger.error(f"Erro em novo_usuario: {str(e)}")
            return render_template('usuarios/form.html', 
                                 roles=roles,
                                 form_data=request.form)
    
    return render_template('usuarios/form.html', roles=roles)

@app.route('/usuarios/dashboard')
@permission_required('manage_access')
@login_required
def dashboard_usuarios():
    """Dashboard avançado de usuários com estatísticas e métricas."""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    
    # Estatísticas gerais
    total_usuarios = User.query.count()
    usuarios_ativos = User.query.filter_by(status='ativo').count()
    usuarios_inativos = User.query.filter_by(status='inativo').count()
    usuarios_bloqueados = User.query.filter_by(status='bloqueado').count()
    usuarios_ldap = User.query.filter_by(ldap_user=True).count()
    usuarios_locais = User.query.filter_by(ldap_user=False).count()
    
    # Usuários criados nos últimos 30 dias
    trinta_dias_atras = datetime.now() - timedelta(days=30)
    novos_usuarios = User.query.filter(User.created_at >= trinta_dias_atras).count()
    
    # Usuários com último login nos últimos 7 dias
    sete_dias_atras = datetime.now() - timedelta(days=7)
    usuarios_ativos_recente = User.query.filter(User.last_login >= sete_dias_atras).count()
    
    # Distribuição por perfis
    perfis_distribuicao = db.session.query(
        Role.nome,
        Role.cor,
        func.count(User.id).label('total_usuarios')
    ).outerjoin(User).group_by(Role.id).all()
    
    # Usuários sem perfil
    usuarios_sem_perfil = User.query.filter_by(role_id=None).count()
    
    # Logins por mês (últimos 6 meses)
    logins_por_mes = []
    for i in range(6):
        mes_atual = datetime.now() - timedelta(days=30*i)
        count = User.query.filter(
            extract('month', User.last_login) == mes_atual.month,
            extract('year', User.last_login) == mes_atual.year
        ).count()
        logins_por_mes.append({
            'mes': mes_atual.strftime('%b/%Y'),
            'count': count
        })
    
    # Top 10 usuários com mais logins
    top_usuarios = User.query.filter(User.login_count > 0).order_by(User.login_count.desc()).limit(10).all()
    
    # Departamentos mais comuns
    departamentos = db.session.query(
        User.departamento,
        func.count(User.id).label('total')
    ).filter(User.departamento.isnot(None)).group_by(User.departamento).order_by(func.count(User.id).desc()).limit(5).all()
    
    estatisticas = {
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'usuarios_inativos': usuarios_inativos,
        'usuarios_bloqueados': usuarios_bloqueados,
        'usuarios_ldap': usuarios_ldap,
        'usuarios_locais': usuarios_locais,
        'novos_usuarios': novos_usuarios,
        'usuarios_ativos_recente': usuarios_ativos_recente,
        'usuarios_sem_perfil': usuarios_sem_perfil
    }
    
    return render_template('usuarios/dashboard.html',
                         estatisticas=estatisticas,
                         perfis_distribuicao=perfis_distribuicao,
                         logins_por_mes=logins_por_mes,
                         top_usuarios=top_usuarios,
                         departamentos=departamentos)

@app.route('/usuarios')
@permission_required('manage_access')
@login_required
def listar_usuarios():
    """Listagem avançada de usuários com filtros e paginação."""
    # Filtros
    busca_login = request.args.get('busca_login', '', type=str)
    busca_nome = request.args.get('busca_nome', '', type=str)
    filtro_status = request.args.get('status', '', type=str)
    filtro_tipo = request.args.get('tipo', '', type=str)  # ldap ou local
    filtro_perfil = request.args.get('perfil_id', '', type=str)
    filtro_departamento = request.args.get('departamento', '', type=str)
    
    # Query base
    query = User.query
    
    # Aplicar filtros
    if busca_login:
        query = query.filter(User.username.ilike(f'%{busca_login}%'))
    if busca_nome:
        query = query.filter(User.nome.ilike(f'%{busca_nome}%'))
    if filtro_status:
        query = query.filter(User.status == filtro_status)
    if filtro_tipo == 'ldap':
        query = query.filter(User.ldap_user == True)
    elif filtro_tipo == 'local':
        query = query.filter(User.ldap_user == False)
    if filtro_perfil:
        query = query.filter(User.role_id == int(filtro_perfil))
    if filtro_departamento:
        query = query.filter(User.departamento.contains(filtro_departamento))
    
    # Ordenação
    ordenacao = request.args.get('sort', 'nome')
    if ordenacao == 'nome':
        query = query.order_by(User.nome)
    elif ordenacao == 'username':
        query = query.order_by(User.username)
    elif ordenacao == 'last_login':
        query = query.order_by(User.last_login.desc())
    elif ordenacao == 'created_at':
        query = query.order_by(User.created_at.desc())
    
    usuarios = query.all()
    
    # Dados para filtros
    perfis_para_filtro = Role.query.all()
    departamentos_para_filtro = db.session.query(User.departamento).filter(User.departamento.isnot(None)).distinct().all()

    return render_template('usuarios/list.html',
                         usuarios=usuarios,
                         perfis_para_filtro=perfis_para_filtro,
                         departamentos_para_filtro=departamentos_para_filtro)

@app.route('/usuarios/bulk-action', methods=['POST'])
@permission_required('manage_access')
@login_required
def bulk_action_usuarios():
    """Operações em lote para usuários."""
    import json
    
    usuario_ids = request.form.getlist('usuario_ids')
    acao = request.form.get('acao')
    
    if not usuario_ids or not acao:
        flash('Selecione usuários e uma ação.', 'danger')
        return redirect(url_for('listar_usuarios'))
    
    try:
        usuarios_afetados = 0
        
        for usuario_id in usuario_ids:
            usuario = User.query.get(int(usuario_id))
            if not usuario:
                continue
                
            # Proteção para admin
            if usuario.username == 'admin' and acao in ['inativar', 'bloquear', 'excluir']:
                continue
            
            if acao == 'ativar':
                if usuario.status != 'ativo':
                    usuario.status = 'ativo'
                    usuarios_afetados += 1
                    
                    # Registrar histórico
                    historico = UserHistory(
                        user_id=usuario.id,
                        acao='status_changed',
                        detalhes=json.dumps({'novo_status': 'ativo', 'bulk_operation': True}),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    
            elif acao == 'inativar':
                if usuario.status != 'inativo':
                    usuario.status = 'inativo'
                    usuarios_afetados += 1
                    
                    # Registrar histórico
                    historico = UserHistory(
                        user_id=usuario.id,
                        acao='status_changed',
                        detalhes=json.dumps({'novo_status': 'inativo', 'bulk_operation': True}),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    
            elif acao == 'bloquear':
                if usuario.status != 'bloqueado':
                    usuario.status = 'bloqueado'
                    usuarios_afetados += 1
                    
                    # Registrar histórico
                    historico = UserHistory(
                        user_id=usuario.id,
                        acao='status_changed',
                        detalhes=json.dumps({'novo_status': 'bloqueado', 'bulk_operation': True}),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    
            elif acao == 'trocar_perfil':
                novo_perfil_id = request.form.get('novo_perfil_id')
                if novo_perfil_id and usuario.role_id != int(novo_perfil_id):
                    perfil_antigo = usuario.role.nome if usuario.role else 'Nenhum'
                    usuario.role_id = int(novo_perfil_id)
                    novo_perfil = Role.query.get(int(novo_perfil_id))
                    usuarios_afetados += 1
                    
                    # Registrar histórico
                    historico = UserHistory(
                        user_id=usuario.id,
                        acao='role_changed',
                        detalhes=json.dumps({
                            'perfil_anterior': perfil_antigo,
                            'novo_perfil': novo_perfil.nome if novo_perfil else 'Nenhum',
                            'bulk_operation': True
                        }),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    
            elif acao == 'excluir':
                if usuario.can_be_deleted():
                    # Registrar histórico antes da exclusão
                    historico = UserHistory(
                        user_id=usuario.id,
                        acao='deleted',
                        detalhes=json.dumps({
                            'username': usuario.username,
                            'nome': usuario.nome,
                            'email': usuario.email,
                            'bulk_operation': True
                        }),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    db.session.flush()  # Para garantir que o histórico seja salvo antes da exclusão
                    
                    db.session.delete(usuario)
                    usuarios_afetados += 1
        
        db.session.commit()
        
        if usuarios_afetados > 0:
            if acao == 'bloquear':
                flash(f'{usuarios_afetados} usuário(s) bloqueado(s) com sucesso!', 'success')
            elif acao == 'ativar':
                flash(f'{usuarios_afetados} usuário(s) ativado(s) com sucesso!', 'success')
            elif acao == 'inativar':
                flash(f'{usuarios_afetados} usuário(s) inativado(s) com sucesso!', 'success')
            elif acao == 'trocar_perfil':
                flash(f'Perfil de {usuarios_afetados} usuário(s) alterado com sucesso!', 'success')
            elif acao == 'excluir':
                flash(f'{usuarios_afetados} usuário(s) excluído(s) com sucesso!', 'success')
            else:
                flash(f'{usuarios_afetados} usuário(s) {acao}(s) com sucesso!', 'success')
        else:
            flash('Nenhum usuário foi modificado.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Erro na operação em lote: {str(e)}', 'danger')
        app.logger.error(f"Erro em bulk_action_usuarios: {str(e)}")
    
    return redirect(url_for('listar_usuarios'))

@app.route('/usuarios/<int:usuario_id>/historico')
@permission_required('manage_access')
@login_required
def historico_usuario(usuario_id):
    """Histórico de alterações do usuário."""
    usuario = User.query.get_or_404(usuario_id)
    
    # Buscar histórico
    historico = UserHistory.query.filter_by(user_id=usuario_id).order_by(UserHistory.created_at.desc()).all()
    
    return render_template('usuarios/historico.html', usuario=usuario, historico=historico)

@app.route('/usuarios/export')
@permission_required('manage_access')
@login_required
def export_usuarios():
    """Exporta usuários para JSON."""
    import json
    from flask import Response
    
    usuarios = User.query.all()
    usuarios_data = []
    
    for usuario in usuarios:
        usuario_dict = usuario.to_dict()
        # Não exportar dados sensíveis
        usuario_dict.pop('password', None)
        usuarios_data.append(usuario_dict)
    
    response_data = {
        'exported_at': datetime.now().isoformat(),
        'exported_by': current_user.username,
        'total_users': len(usuarios_data),
        'users': usuarios_data
    }
    
    response = Response(
        json.dumps(response_data, indent=2, ensure_ascii=False),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=usuarios_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        }
    )
    
    return response

@app.route('/usuarios/import', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def import_usuarios():
    """Importa usuários de arquivo JSON."""
    if request.method == 'GET':
        return render_template('usuarios/import.html')
    
    import json
    from werkzeug.security import generate_password_hash
    
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('import_usuarios'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('import_usuarios'))
    
    try:
        data = json.load(file)
        usuarios_importados = 0
        usuarios_atualizados = 0
        erros = []
        
        for user_data in data.get('users', []):
            try:
                # Verificar se usuário já existe
                usuario_existente = User.query.filter_by(username=user_data['username']).first()
                
                if usuario_existente:
                    # Atualizar usuário existente (exceto admin)
                    if usuario_existente.username != 'admin':
                        usuario_existente.nome = user_data.get('nome', usuario_existente.nome)
                        usuario_existente.email = user_data.get('email', usuario_existente.email)
                        usuario_existente.telefone = user_data.get('telefone')
                        usuario_existente.departamento = user_data.get('departamento')
                        usuario_existente.cargo = user_data.get('cargo')
                        
                        # Buscar e definir role
                        if user_data.get('role_name'):
                            role = Role.query.filter_by(nome=user_data['role_name']).first()
                            if role:
                                usuario_existente.role_id = role.id
                        
                        usuarios_atualizados += 1
                        
                        # Registrar histórico
                        historico = UserHistory(
                            user_id=usuario_existente.id,
                            acao='updated',
                            detalhes=json.dumps({'import_operation': True, 'updated_fields': list(user_data.keys())}),
                            usuario=current_user.username,
                            ip_address=request.remote_addr,
                            user_agent=request.headers.get('User-Agent', '')[:255]
                        )
                        db.session.add(historico)
                else:
                    # Criar novo usuário
                    role = None
                    if user_data.get('role_name'):
                        role = Role.query.filter_by(nome=user_data['role_name']).first()
                    
                    novo_usuario = User(
                        username=user_data['username'],
                        nome=user_data['nome'],
                        email=user_data['email'],
                        password=generate_password_hash('123456'),  # Senha padrão
                        status=user_data.get('status', 'ativo'),
                        telefone=user_data.get('telefone'),
                        departamento=user_data.get('departamento'),
                        cargo=user_data.get('cargo'),
                        role_id=role.id if role else None,
                        ldap_user=user_data.get('ldap_user', False),
                        created_by=current_user.username
                    )
                    
                    db.session.add(novo_usuario)
                    db.session.flush()  # Para obter o ID
                    usuarios_importados += 1
                    
                    # Registrar histórico
                    historico = UserHistory(
                        user_id=novo_usuario.id,
                        acao='created',
                        detalhes=json.dumps({'import_operation': True}),
                        usuario=current_user.username,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')[:255]
                    )
                    db.session.add(historico)
                    
            except Exception as user_error:
                erros.append(f"Erro ao processar usuário {user_data.get('username', 'desconhecido')}: {str(user_error)}")
        
        db.session.commit()
        
        flash(f'Importação concluída! {usuarios_importados} novos usuários, {usuarios_atualizados} atualizados.', 'success')
        
        if erros:
            for erro in erros[:5]:  # Mostrar apenas os 5 primeiros erros
                flash(erro, 'warning')
                
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
        app.logger.error(f"Erro em import_usuarios: {str(e)}")
    
    return redirect(url_for('listar_usuarios')) 

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def editar_usuario(usuario_id):
    """Edição avançada de usuário com histórico de alterações."""
    import json
    from werkzeug.security import generate_password_hash
    
    usuario = User.query.get_or_404(usuario_id)
    roles = Role.query.filter_by(ativo=True).all()
    
    if request.method == 'POST':
        # Guardar valores originais para o histórico
        valores_originais = {
            'username': usuario.username,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'departamento': usuario.departamento,
            'cargo': usuario.cargo,
            'observacoes': usuario.observacoes,
            'status': usuario.status,
            'role_id': usuario.role_id
        }
        
        # Campos do formulário
        username = request.form.get('username', '').strip()
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        telefone = request.form.get('telefone', '').strip()
        departamento = request.form.get('departamento', '').strip()
        cargo = request.form.get('cargo', '').strip()
        observacoes = request.form.get('observacoes', '').strip()
        status = request.form.get('status', usuario.status)
        role_id = request.form.get('role_id')
        
        # Validações
        erros = []
        
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        elif User.query.filter(User.username == username, User.id != usuario.id).first():
            erros.append('Nome de usuário já existe.')
        elif len(username) < 3:
            erros.append('Nome de usuário deve ter pelo menos 3 caracteres.')
            
        if not nome:
            erros.append('Nome completo é obrigatório.')
        elif len(nome) < 2:
            erros.append('Nome deve ter pelo menos 2 caracteres.')
            
        if not email:
            erros.append('E-mail é obrigatório.')
        elif User.query.filter(User.email == email, User.id != usuario.id).first():
            erros.append('E-mail já está em uso.')
        elif '@' not in email or '.' not in email:
            erros.append('E-mail deve ter formato válido.')
            
        if password and len(password) < 6:
            erros.append('Nova senha deve ter pelo menos 6 caracteres.')
            
        if telefone and len(telefone) < 8:
            erros.append('Telefone deve ter pelo menos 8 dígitos.')
            
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('usuarios/form.html', 
                                 usuario=usuario, 
                                 roles=roles,
                                 form_data=request.form)
        
        try:
            # Rastrear alterações
            alteracoes = []
            
            if username != usuario.username:
                alteracoes.append(f"Username: {usuario.username} → {username}")
                usuario.username = username
                
            if nome != usuario.nome:
                alteracoes.append(f"Nome: {usuario.nome} → {nome}")
                usuario.nome = nome
                
            if email != usuario.email:
                alteracoes.append(f"Email: {usuario.email} → {email}")
                usuario.email = email
                
            if telefone != usuario.telefone:
                alteracoes.append(f"Telefone: {usuario.telefone or 'Vazio'} → {telefone or 'Vazio'}")
                usuario.telefone = telefone or None
                
            if departamento != usuario.departamento:
                alteracoes.append(f"Departamento: {usuario.departamento or 'Vazio'} → {departamento or 'Vazio'}")
                usuario.departamento = departamento or None
                
            if cargo != usuario.cargo:
                alteracoes.append(f"Cargo: {usuario.cargo or 'Vazio'} → {cargo or 'Vazio'}")
                usuario.cargo = cargo or None
                
            if observacoes != usuario.observacoes:
                alteracoes.append("Observações alteradas")
                usuario.observacoes = observacoes or None
                
            if status != usuario.status:
                alteracoes.append(f"Status: {usuario.status} → {status}")
                usuario.status = status
            
            # Senha
            if password:
                usuario.password = generate_password_hash(password)
                alteracoes.append("Senha alterada")
            
            # Proteção para admin
            if usuario.username == 'admin':
                admin_role = Role.query.filter_by(nome='admin').first()
                if admin_role and usuario.role_id != admin_role.id:
                    usuario.role_id = admin_role.id
                    alteracoes.append("Perfil admin forçado para usuário admin")
            elif role_id and int(role_id) != usuario.role_id:
                role_anterior = Role.query.get(usuario.role_id).nome if usuario.role_id else 'Nenhum'
                nova_role = Role.query.get(int(role_id))
                if nova_role:
                    alteracoes.append(f"Perfil: {role_anterior} → {nova_role.nome}")
                    usuario.role_id = int(role_id)
            
            # Atualizar timestamp
            usuario.updated_at = db.func.now()
            
            # Registrar histórico se houver alterações
            if alteracoes:
                historico = UserHistory(
                    user_id=usuario.id,
                    acao='updated',
                    detalhes=json.dumps({
                        'alteracoes': alteracoes,
                        'updated_by': current_user.username
                    }),
                    usuario=current_user.username,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', '')[:255]
                )
                db.session.add(historico)
            
            db.session.commit()
            
            if alteracoes:
                flash(f'Usuário "{username}" atualizado com sucesso! ({len(alteracoes)} alterações)', 'success')
            else:
                flash('Nenhuma alteração foi feita.', 'info')
                
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar usuário: {str(e)}', 'danger')
            app.logger.error(f"Erro em editar_usuario: {str(e)}")
            return render_template('usuarios/form.html', 
                                 usuario=usuario, 
                                 roles=roles,
                                 form_data=request.form)
    
    return render_template('usuarios/form.html', usuario=usuario, roles=roles)

@app.route('/usuarios/<int:usuario_id>/excluir', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def excluir_usuario(usuario_id):
    """Exclusão de usuário. Protegida por manage_access."""
    usuario = User.query.get_or_404(usuario_id)
    
    # 🔒 PROTEÇÃO CRÍTICA: Não permitir exclusão do admin
    if usuario.username == 'admin':
        flash('O usuário admin não pode ser excluído por questões de segurança.', 'danger')
        return redirect(url_for('listar_usuarios'))
    
    # 🔒 PROTEÇÃO: Não permitir que o usuário se exclua
    if usuario.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'danger')
        return redirect(url_for('listar_usuarios'))
    
    if request.method == 'POST':
        # Log da ação para auditoria
        app.logger.warning(f'Usuário {current_user.username} excluiu o usuário {usuario.username} (ID: {usuario.id})')
        
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
        
        try:
            from werkzeug.security import generate_password_hash
            usuario.password = generate_password_hash(nova_senha)
            
            # Registrar histórico
            historico = UserHistory(
                user_id=usuario.id,
                acao='password_reset',
                detalhes=json.dumps({
                    'reset_by': current_user.username,
                    'reset_method': 'manual'
                }),
                usuario=current_user.username,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            db.session.add(historico)
            db.session.commit()
            
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('listar_usuarios'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao redefinir senha: {str(e)}', 'danger')
            app.logger.error(f"Erro em resetar_senha_usuario: {str(e)}")
            
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

# ===== FUNCIONALIDADES AVANÇADAS DE GERENCIAMENTO DE ROLES =====

@app.route('/perfis/dashboard')
@permission_required('manage_access')
@login_required
def dashboard_perfis():
    """Dashboard avançado de gestão de perfis com estatísticas."""
    from sqlalchemy import func
    from models import RoleHistory, RoleTemplate
    
    # Estatísticas básicas
    total_roles = Role.query.count()
    roles_ativos = Role.query.filter_by(ativo=True).count()
    roles_ldap = Role.query.filter_by(is_ldap_role=True).count()
    usuarios_por_role = db.session.query(
        Role.nome, func.count(User.id).label('usuarios')
    ).outerjoin(User).group_by(Role.id, Role.nome).all()
    
    # Histórico recente
    historico_recente = RoleHistory.query.order_by(
        RoleHistory.timestamp.desc()
    ).limit(10).all()
    
    # Permissions por categoria
    perms_por_categoria = db.session.query(
        Permission.categoria, func.count(Permission.id).label('total')
    ).group_by(Permission.categoria).all()
    
    # Templates disponíveis
    templates = RoleTemplate.query.filter_by(ativo=True).all()
    
    return render_template('perfis/dashboard.html',
                         total_roles=total_roles,
                         roles_ativos=roles_ativos,
                         roles_ldap=roles_ldap,
                         usuarios_por_role=usuarios_por_role,
                         historico_recente=historico_recente,
                         perms_por_categoria=perms_por_categoria,
                         templates=templates)

@app.route('/perfis/<int:perfil_id>/clonar', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def clonar_perfil(perfil_id):
    """Clona um perfil existente com todas as suas permissões."""
    perfil_origem = Role.query.get_or_404(perfil_id)
    
    if request.method == 'POST':
        nome_novo = request.form['nome']
        descricao_nova = request.form.get('descricao', f"Clone de {perfil_origem.nome}")
        
        # Validações
        if Role.query.filter_by(nome=nome_novo).first():
            flash('Já existe um perfil com esse nome.', 'danger')
            return render_template('perfis/clonar.html', perfil=perfil_origem)
        
        # Criar novo perfil
        novo_perfil = Role(
            nome=nome_novo,
            descricao=descricao_nova,
            cor=perfil_origem.cor,
            icone=perfil_origem.icone,
            prioridade=perfil_origem.prioridade,
            parent_id=perfil_origem.parent_id,
            created_by=current_user.username
        )
        
        # Clonar permissões
        for perm in perfil_origem.permissions:
            novo_perfil.permissions.append(perm)
        
        db.session.add(novo_perfil)
        db.session.commit()
        
        # Registrar no histórico
        from models import RoleHistory
        import json
        historico = RoleHistory(
            role_id=novo_perfil.id,
            acao='cloned',
            detalhes=json.dumps({
                'origem_id': perfil_origem.id,
                'origem_nome': perfil_origem.nome,
                'permissoes_clonadas': len(perfil_origem.permissions)
            }),
            usuario=current_user.username
        )
        db.session.add(historico)
        db.session.commit()
        
        flash(f'Perfil "{nome_novo}" clonado com sucesso de "{perfil_origem.nome}"!', 'success')
        return redirect(url_for('listar_perfis'))
    
    return render_template('perfis/clonar.html', perfil=perfil_origem)

@app.route('/perfis/bulk-action', methods=['POST'])
@permission_required('manage_access')
@login_required
def bulk_action_perfis():
    """Ações em lote para múltiplos perfis."""
    action = request.form.get('action')
    perfis_ids = request.form.getlist('perfis_ids')
    
    if not perfis_ids:
        flash('Nenhum perfil selecionado.', 'warning')
        return redirect(url_for('listar_perfis'))
    
    perfis = Role.query.filter(Role.id.in_(perfis_ids)).all()
    
    if action == 'ativar':
        for perfil in perfis:
            if perfil.nome != 'admin':  # Não alterar admin
                perfil.ativo = True
        flash(f'{len(perfis)} perfis ativados com sucesso!', 'success')
        
    elif action == 'desativar':
        for perfil in perfis:
            if perfil.nome != 'admin':  # Não desativar admin
                perfil.ativo = False
        flash(f'{len(perfis)} perfis desativados com sucesso!', 'success')
        
    elif action == 'excluir':
        excluidos = 0
        for perfil in perfis:
            can_delete, msg = perfil.can_be_deleted()
            if can_delete:
                db.session.delete(perfil)
                excluidos += 1
        flash(f'{excluidos} perfis excluídos com sucesso!', 'success')
        
    db.session.commit()
    return redirect(url_for('listar_perfis'))

@app.route('/perfis/templates')
@permission_required('manage_access')
@login_required
def listar_templates():
    """Lista templates de perfis disponíveis."""
    from models import RoleTemplate
    templates = RoleTemplate.query.filter_by(ativo=True).all()
    return render_template('perfis/templates.html', templates=templates)

@app.route('/perfis/criar-do-template/<int:template_id>')
@permission_required('manage_access')
@login_required
def criar_do_template(template_id):
    """Cria um perfil baseado em template."""
    from models import RoleTemplate
    import json
    
    template = RoleTemplate.query.get_or_404(template_id)
    config = json.loads(template.config_json)
    
    # Criar perfil baseado no template
    novo_perfil = Role(
        nome=f"{template.nome}_{datetime.now().strftime('%Y%m%d_%H%M')}",
        descricao=config.get('descricao', template.descricao),
        cor=config.get('cor', '#6c757d'),
        icone=config.get('icone', 'bi-person'),
        prioridade=config.get('prioridade', 0),
        created_by=current_user.username
    )
    
    # Adicionar permissões do template
    for perm_nome in config.get('permissions', []):
        perm = Permission.query.filter_by(nome=perm_nome).first()
        if perm:
            novo_perfil.permissions.append(perm)
    
    db.session.add(novo_perfil)
    db.session.commit()
    
    flash(f'Perfil criado com sucesso baseado no template "{template.nome}"!', 'success')
    return redirect(url_for('editar_perfil', perfil_id=novo_perfil.id))

@app.route('/perfis/export')
@permission_required('manage_access')
@login_required
def export_perfis():
    """Exporta perfis para JSON."""
    import json
    from flask import make_response
    
    perfis = Role.query.all()
    export_data = {
        'timestamp': datetime.now().isoformat(),
        'exported_by': current_user.username,
        'perfis': [perfil.to_dict() for perfil in perfis]
    }
    
    response = make_response(json.dumps(export_data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=perfis_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    return response

@app.route('/perfis/import', methods=['GET', 'POST'])
@permission_required('manage_access')
@login_required
def import_perfis():
    """Importa perfis de arquivo JSON."""
    if request.method == 'POST':
        import json
        from models import RoleHistory
        
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        try:
            dados = json.loads(arquivo.read().decode('utf-8'))
            importados = 0
            
            for perfil_data in dados.get('perfis', []):
                # Verificar se já existe
                if Role.query.filter_by(nome=perfil_data['nome']).first():
                    continue
                
                # Criar perfil
                perfil = Role(
                    nome=perfil_data['nome'],
                    descricao=perfil_data.get('descricao', ''),
                    cor=perfil_data.get('cor', '#6c757d'),
                    icone=perfil_data.get('icone', 'bi-person'),
                    ativo=perfil_data.get('ativo', True),
                    prioridade=perfil_data.get('prioridade', 0),
                    created_by=current_user.username
                )
                
                # Adicionar permissões
                for perm_nome in perfil_data.get('permissions', []):
                    perm = Permission.query.filter_by(nome=perm_nome).first()
                    if perm:
                        perfil.permissions.append(perm)
                
                db.session.add(perfil)
                importados += 1
            
            db.session.commit()
            flash(f'{importados} perfis importados com sucesso!', 'success')
            
        except Exception as e:
            flash(f'Erro ao importar arquivo: {str(e)}', 'danger')
    
    return render_template('perfis/import.html')

@app.route('/perfis/<int:perfil_id>/historico')
@permission_required('manage_access')
@login_required
def historico_perfil(perfil_id):
    """Visualiza histórico de alterações de um perfil."""
    from models import RoleHistory
    perfil = Role.query.get_or_404(perfil_id)
    historico = RoleHistory.query.filter_by(role_id=perfil_id).order_by(
        RoleHistory.timestamp.desc()
    ).all()
    
    return render_template('perfis/historico.html', perfil=perfil, historico=historico)

@app.route('/perfis/assistente')
@permission_required('manage_access')
@login_required
def assistente_perfil():
    """Assistente para criação de perfis baseado em cenários."""
    scenarios = [
        {
            'id': 'admin_dept',
            'nome': 'Administrador de Departamento',
            'descricao': 'Gerencia usuários e dados do seu departamento',
            'permissions': ['manage_registros', 'manage_responsaveis', 'send_alerts'],
            'cor': '#28a745',
            'icone': 'bi-building'
        },
        {
            'id': 'operador',
            'nome': 'Operador de Sistema',
            'descricao': 'Acesso operacional para tarefas do dia a dia',
            'permissions': ['manage_registros', 'send_alerts'],
            'cor': '#17a2b8',
            'icone': 'bi-gear'
        },
        {
            'id': 'visualizador',
            'nome': 'Visualizador',
            'descricao': 'Apenas leitura de dados e relatórios',
            'permissions': [],
            'cor': '#6c757d',
            'icone': 'bi-eye'
        },
        {
            'id': 'auditor',
            'nome': 'Auditor',
            'descricao': 'Acesso a logs e auditoria do sistema',
            'permissions': ['manage_access'],
            'cor': '#fd7e14',
            'icone': 'bi-shield-check'
        }
    ]
    
    return render_template('perfis/assistente.html', scenarios=scenarios)

@app.route('/perfis/criar-cenario', methods=['POST'])
@permission_required('manage_access')
@login_required
def criar_perfil_cenario():
    """Cria perfil baseado em cenário do assistente."""
    from models import RoleHistory
    import json
    
    scenario_id = request.form.get('scenario')
    nome_customizado = request.form.get('nome')
    descricao_customizada = request.form.get('descricao')
    
    # Mapear cenários (seria melhor ter isso em BD)
    scenarios_map = {
        'admin_dept': {
            'permissions': ['manage_registros', 'manage_responsaveis', 'send_alerts'],
            'cor': '#28a745',
            'icone': 'bi-building'
        },
        'operador': {
            'permissions': ['manage_registros', 'send_alerts'],
            'cor': '#17a2b8',
            'icone': 'bi-gear'
        },
        'visualizador': {
            'permissions': [],
            'cor': '#6c757d',
            'icone': 'bi-eye'
        },
        'auditor': {
            'permissions': ['manage_access'],
            'cor': '#fd7e14',
            'icone': 'bi-shield-check'
        }
    }
    
    if scenario_id not in scenarios_map:
        flash('Cenário inválido.', 'danger')
        return redirect(url_for('assistente_perfil'))
    
    scenario = scenarios_map[scenario_id]
    
    # Criar perfil
    perfil = Role(
        nome=nome_customizado or f"{scenario_id}_{datetime.now().strftime('%Y%m%d')}",
        descricao=descricao_customizada or f"Perfil criado via assistente - {scenario_id}",
        cor=scenario['cor'],
        icone=scenario['icone'],
        created_by=current_user.username
    )
    
    # Adicionar permissões
    for perm_nome in scenario['permissions']:
        perm = Permission.query.filter_by(nome=perm_nome).first()
        if perm:
            perfil.permissions.append(perm)
    
    db.session.add(perfil)
    db.session.commit()
    
    # Registrar histórico
    historico = RoleHistory(
        role_id=perfil.id,
        acao='created_by_wizard',
        detalhes=json.dumps({
            'scenario': scenario_id,
            'permissions_added': len(scenario['permissions'])
        }),
        usuario=current_user.username
    )
    db.session.add(historico)
    db.session.commit()
    
    flash(f'Perfil "{perfil.nome}" criado com sucesso via assistente!', 'success')
    return redirect(url_for('editar_perfil', perfil_id=perfil.id))

@app.route('/perfis/relatorio-permissoes')
@permission_required('manage_access')
@login_required
def relatorio_permissoes():
    """Relatório detalhado de permissões por perfil."""
    from sqlalchemy import func
    
    # Estatísticas gerais
    total_perfis = Role.query.count()
    total_permissoes = Permission.query.count()
    perfis_ativos = Role.query.filter_by(ativo=True).count()
    usuarios_com_perfis = User.query.filter(User.roles.any()).count()
    
    estatisticas = {
        'total_perfis': total_perfis,
        'total_permissoes': total_permissoes,
        'perfis_ativos': perfis_ativos,
        'usuarios_com_perfis': usuarios_com_perfis
    }
    
    # Dados para filtros
    todos_perfis = Role.query.all()
    todas_permissoes = Permission.query.all()
    
    # Matriz de permissões
    matriz_permissoes = []
    for perfil in todos_perfis:
        perfil_data = {
            'perfil': perfil,
            'permissoes': perfil.permissions
        }
        matriz_permissoes.append(perfil_data)
    
    # Relatório de permissões por role
    roles_permissions = db.session.query(
        Role.nome,
        Role.descricao,
        Role.ativo,
        func.count(Permission.id).label('total_permissions')
    ).outerjoin(Role.permissions).group_by(Role.id).all()
    
    # Permissões não utilizadas
    unused_permissions = db.session.query(Permission).outerjoin(
        Permission.roles
    ).filter(~Permission.roles.any()).all()
    
    # Roles sem permissões
    roles_without_permissions = db.session.query(Role).outerjoin(
        Role.permissions
    ).filter(~Role.permissions.any()).all()
    
    return render_template('perfis/relatorio.html',
                         estatisticas=estatisticas,
                         todos_perfis=todos_perfis,
                         todas_permissoes=todas_permissoes,
                         matriz_permissoes=matriz_permissoes,
                         roles_permissions=roles_permissions,
                         unused_permissions=unused_permissions,
                         roles_without_permissions=roles_without_permissions)

@app.route('/perfis/<int:perfil_id>/toggle-status')
@permission_required('manage_access')
@login_required
def toggle_perfil_status(perfil_id):
    """Alterna status ativo/inativo do perfil."""
    perfil = Role.query.get_or_404(perfil_id)
    
    if perfil.nome == 'admin':
        flash('Não é possível desativar o perfil admin.', 'danger')
        return redirect(url_for('listar_perfis'))
    
    perfil.ativo = not perfil.ativo
    status = 'ativado' if perfil.ativo else 'desativado'
    
    # Registrar no histórico
    from models import RoleHistory
    import json
    historico = RoleHistory(
        role_id=perfil.id,
        acao='status_changed',
        detalhes=json.dumps({'novo_status': perfil.ativo}),
        usuario=current_user.username
    )
    db.session.add(historico)
    db.session.commit()
    
    flash(f'Perfil "{perfil.nome}" {status} com sucesso!', 'success')
    return redirect(url_for('listar_perfis')) 