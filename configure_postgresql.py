#!/usr/bin/env python3
"""
Script para configuração interativa e segura do PostgreSQL
Permite ao usuário definir suas próprias credenciais de forma segura
"""

import os
import sys
import getpass
import subprocess
import platform
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime mensagem de erro"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprime mensagem de aviso"""
    print(f"⚠️  {message}")

def print_info(message):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {message}")

def get_user_input(prompt, default=None, password=False):
    """Obtém entrada do usuário de forma segura"""
    if default:
        prompt = f"{prompt} (padrão: {default}): "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default

def check_postgresql_installed():
    """Verifica se PostgreSQL está instalado"""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_postgresql():
    """Instala PostgreSQL baseado no sistema operacional"""
    system = platform.system().lower()
    
    print_info("Instalando PostgreSQL...")
    
    if system == "windows":
        print_warning("No Windows, você precisa instalar PostgreSQL manualmente.")
        print_info("Baixe de: https://www.postgresql.org/download/windows/")
        print_info("Ou use: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads")
        return False
    elif system == "linux":
        # Detectar distribuição
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                if 'ubuntu' in content.lower() or 'debian' in content.lower():
                    cmd = ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', 'postgresql', 'postgresql-contrib']
                elif 'suse' in content.lower():
                    cmd = ['sudo', 'zypper', 'install', '-y', 'postgresql', 'postgresql-server']
                elif 'centos' in content.lower() or 'rhel' in content.lower() or 'fedora' in content.lower():
                    cmd = ['sudo', 'dnf', 'install', '-y', 'postgresql', 'postgresql-server']
                else:
                    print_warning("Distribuição Linux não reconhecida. Instale PostgreSQL manualmente.")
                    return False
                
                print_info(f"Executando: {' '.join(cmd)}")
                result = subprocess.run(cmd, shell=True)
                return result.returncode == 0
        except FileNotFoundError:
            print_warning("Não foi possível detectar a distribuição Linux.")
            return False
    else:
        print_warning(f"Sistema operacional não suportado: {system}")
        return False

def create_postgresql_user(username, password, database):
    """Cria usuário e banco no PostgreSQL"""
    try:
        # Comandos SQL para criar usuário e banco
        sql_commands = [
            f"CREATE USER {username} WITH PASSWORD '{password}';",
            f"CREATE DATABASE {database} OWNER {username};",
            f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {username};"
        ]
        
        for command in sql_commands:
            result = subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', command], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print_warning(f"Comando falhou: {command}")
                print_warning(f"Erro: {result.stderr}")
        
        return True
    except Exception as e:
        print_error(f"Erro ao criar usuário/banco: {e}")
        return False

def create_env_file(username, password, database, host, port):
    """Cria arquivo .env com as credenciais"""
    try:
        # Gerar SECRET_KEY aleatória
        import secrets
        secret_key = secrets.token_hex(32)
        
        env_content = f"""# Configurações do Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY={secret_key}

# Configurações do Banco de Dados PostgreSQL
DATABASE_URL=postgresql://{username}:{password}@{host}:{port}/{database}

# Configurações de Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_de_app
MAIL_DEFAULT_SENDER=seu_email@gmail.com

# Configurações de Autenticação
AUTH_MODE=banco

# Configurações de Sessão
PERMANENT_SESSION_LIFETIME=3600

# Configurações de Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Configurações do Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=America/Sao_Paulo
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print_success("Arquivo .env criado com sucesso!")
        return True
    except Exception as e:
        print_error(f"Erro ao criar arquivo .env: {e}")
        return False

def main():
    """Função principal"""
    print_header("CONFIGURAÇÃO SEGURA DO POSTGRESQL")
    
    print_info("Este script irá configurar o PostgreSQL de forma segura.")
    print_info("Você definirá suas próprias credenciais.")
    print()
    
    # Verificar se PostgreSQL está instalado
    if not check_postgresql_installed():
        print_warning("PostgreSQL não encontrado!")
        response = input("Deseja instalar o PostgreSQL? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            if not install_postgresql():
                print_error("Falha ao instalar PostgreSQL. Instale manualmente.")
                return False
        else:
            print_info("Instale o PostgreSQL manualmente e execute este script novamente.")
            return False
    
    print_success("PostgreSQL encontrado!")
    print()
    
    # Obter credenciais do usuário
    print_info("Defina as credenciais do banco de dados:")
    print()
    
    username = get_user_input("Nome do usuário PostgreSQL", "certificados_user")
    password = get_user_input("Senha do usuário PostgreSQL", password=True)
    database = get_user_input("Nome do banco de dados", "certificados_db")
    host = get_user_input("Host PostgreSQL", "localhost")
    port = get_user_input("Porta PostgreSQL", "5432")
    
    print()
    print_info("Resumo da configuração:")
    print(f"  Usuário: {username}")
    print(f"  Banco: {database}")
    print(f"  Host: {host}")
    print(f"  Porta: {port}")
    print()
    
    # Confirmar configuração
    confirm = input("Confirma esta configuração? (s/n): ").lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print_info("Configuração cancelada.")
        return False
    
    # Criar usuário e banco (apenas no Linux)
    if platform.system().lower() == "linux":
        print_info("Criando usuário e banco de dados...")
        if not create_postgresql_user(username, password, database):
            print_warning("Não foi possível criar usuário/banco automaticamente.")
            print_info("Crie manualmente no PostgreSQL:")
            print(f"  CREATE USER {username} WITH PASSWORD '{password}';")
            print(f"  CREATE DATABASE {database} OWNER {username};")
            print(f"  GRANT ALL PRIVILEGES ON DATABASE {database} TO {username};")
    
    # Criar arquivo .env
    print_info("Criando arquivo .env...")
    if create_env_file(username, password, database, host, port):
        print_success("Configuração concluída com sucesso!")
        print()
        print_info("Próximos passos:")
        print("1. Configure o arquivo .env com suas configurações de email")
        print("2. Execute: python quick_setup.py setup")
        print("3. Execute: python manage_db.py create-admin")
        print("4. Execute: python app.py")
        return True
    else:
        print_error("Falha na configuração.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nConfiguração cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
