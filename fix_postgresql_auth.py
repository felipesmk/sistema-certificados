#!/usr/bin/env python3
"""
Script para corrigir configuração de autenticação do PostgreSQL no SUSE Linux
Resolve problemas de autenticação Ident e configura autenticação por senha
"""

import os
import sys
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

def check_suse():
    """Verifica se é SUSE Linux"""
    if not os.path.exists('/etc/os-release'):
        return False
    
    with open('/etc/os-release', 'r') as f:
        content = f.read().lower()
        return 'suse' in content or 'opensuse' in content

def find_postgresql_config():
    """Encontra o arquivo de configuração do PostgreSQL"""
    possible_paths = [
        '/var/lib/pgsql/data/pg_hba.conf',
        '/etc/postgresql/*/main/pg_hba.conf',
        '/var/lib/postgresql/*/data/pg_hba.conf',
        '/opt/postgresql/*/data/pg_hba.conf'
    ]
    
    for path_pattern in possible_paths:
        import glob
        matches = glob.glob(path_pattern)
        if matches:
            return matches[0]
    
    return None

def backup_config_file(config_file):
    """Faz backup do arquivo de configuração"""
    backup_file = f"{config_file}.backup"
    try:
        import shutil
        shutil.copy2(config_file, backup_file)
        print_success(f"Backup criado: {backup_file}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar backup: {e}")
        return False

def fix_pg_hba_conf(config_file):
    """Corrige o arquivo pg_hba.conf"""
    try:
        # Ler arquivo atual
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        # Criar backup
        if not backup_config_file(config_file):
            return False
        
        # Substituir linhas problemáticas
        new_lines = []
        for line in lines:
            # Comentar linhas com autenticação ident
            if 'ident' in line.lower() and not line.strip().startswith('#'):
                new_lines.append(f"# {line.strip()}  # Comentado pelo script de correção\n")
            else:
                new_lines.append(line)
        
        # Adicionar configurações corretas no final
        new_lines.extend([
            "\n# Configurações corrigidas para autenticação por senha\n",
            "local   all             all                                     md5\n",
            "host    all             all             127.0.0.1/32            md5\n",
            "host    all             all             ::1/128                 md5\n",
            "host    all             all             0.0.0.0/0               md5\n"
        ])
        
        # Escrever arquivo corrigido
        with open(config_file, 'w') as f:
            f.writelines(new_lines)
        
        print_success("Arquivo pg_hba.conf corrigido!")
        return True
        
    except Exception as e:
        print_error(f"Erro ao corrigir pg_hba.conf: {e}")
        return False

def restart_postgresql():
    """Reinicia o serviço PostgreSQL"""
    print_info("Reiniciando PostgreSQL...")
    
    # Tentar diferentes comandos de reinicialização
    restart_commands = [
        ['sudo', 'systemctl', 'restart', 'postgresql'],
        ['sudo', 'systemctl', 'restart', 'postgresql.service'],
        ['sudo', 'service', 'postgresql', 'restart'],
        ['sudo', '/etc/init.d/postgresql', 'restart']
    ]
    
    for cmd in restart_commands:
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print_success("PostgreSQL reiniciado com sucesso!")
                return True
        except FileNotFoundError:
            continue
    
    print_warning("Não foi possível reiniciar automaticamente.")
    print_info("Reinicie manualmente com: sudo systemctl restart postgresql")
    return False

def test_connection(username, password, database):
    """Testa conexão com o banco"""
    try:
        # Definir variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Testar conexão
        cmd = ['psql', '-h', 'localhost', '-U', username, '-d', database, '-c', 'SELECT 1;']
        result = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print_success("Conexão com PostgreSQL testada com sucesso!")
            return True
        else:
            print_error(f"Erro na conexão: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao testar conexão: {e}")
        return False

def main():
    """Função principal"""
    print_header("CORREÇÃO DE AUTENTICAÇÃO POSTGRESQL - SUSE LINUX")
    
    # Verificar se é SUSE
    if not check_suse():
        print_warning("Este script é específico para SUSE Linux.")
        print_info("Execute apenas em sistemas SUSE/OpenSUSE.")
        return False
    
    print_success("Sistema SUSE detectado!")
    print()
    
    # Encontrar arquivo de configuração
    config_file = find_postgresql_config()
    if not config_file:
        print_error("Arquivo pg_hba.conf não encontrado!")
        print_info("Verifique se o PostgreSQL está instalado corretamente.")
        return False
    
    print_info(f"Arquivo de configuração encontrado: {config_file}")
    print()
    
    # Corrigir configuração
    print_info("Corrigindo configuração de autenticação...")
    if not fix_pg_hba_conf(config_file):
        return False
    
    # Reiniciar PostgreSQL
    if not restart_postgresql():
        print_warning("Continue com reinicialização manual.")
    
    print()
    print_success("Configuração corrigida!")
    print()
    print_info("Próximos passos:")
    print("1. Se não reiniciou automaticamente, execute:")
    print("   sudo systemctl restart postgresql")
    print("2. Teste a conexão:")
    print("   python configure_postgresql.py")
    print("3. Execute o setup:")
    print("   python quick_setup.py setup")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
