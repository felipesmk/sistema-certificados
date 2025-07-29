# Configuração do Gunicorn para produção
import multiprocessing

# Configurações básicas
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Configurações de logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configurações de processo
preload_app = True
daemon = False
pidfile = "gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configurações de SSL (descomente se usar HTTPS)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

def when_ready(server):
    """Chamado quando o servidor está pronto para receber conexões"""
    server.log.info("Servidor Gunicorn iniciado e pronto para conexões")

def on_starting(server):
    """Chamado quando o servidor está iniciando"""
    server.log.info("Iniciando servidor Gunicorn...")

def on_reload(server):
    """Chamado quando o servidor é recarregado"""
    server.log.info("Servidor Gunicorn recarregado")

def worker_int(worker):
    """Chamado quando um worker é interrompido"""
    worker.log.info("Worker interrompido")

def pre_fork(server, worker):
    """Chamado antes de criar um worker"""
    server.log.info("Criando worker...")

def post_fork(server, worker):
    """Chamado após criar um worker"""
    server.log.info(f"Worker {worker.pid} criado")

def post_worker_init(worker):
    """Chamado após inicializar um worker"""
    worker.log.info(f"Worker {worker.pid} inicializado") 