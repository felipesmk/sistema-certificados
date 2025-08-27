#!/usr/bin/env python3
"""
Script específico para corrigir autenticação PostgreSQL no SUSE Linux
Versão simplificada e direta
"""

import os
import sys
import subprocess

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_suse():
    """Verifica se é SUSE Linux"""
    if not os.path.exists('/etc/os-release'):
        return False
    
    with open('/etc/os-release', 'r') as f:
        content = f.read().lower()
        return 'suse' in content or 'opensuse' in content

def fix_postgresql_auth():
    """Corrige autenticação PostgreSQL no SUSE"""
    print_header("CORREÇÃO POSTGRESQL - SUSE LINUX")
    
    if not check_suse():
        print_error("Este script é específico para SUSE Linux!")
        return False
    
    print_success("Sistema SUSE detectado!")
    
    # Caminho padrão do SUSE
    config_file = '/var/lib/pgsql/data/pg_hba.conf'
    
    if not os.path.exists(config_file):
        print_error(f"Arquivo não encontrado: {config_file}")
        return False
    
    print_info(f"Arquivo encontrado: {config_file}")
    
    try:
        # 1. Fazer backup
        print_info("Criando backup...")
        backup_cmd = ['sudo', '-u', 'postgres', 'cp', config_file, f'{config_file}.backup']
        result = subprocess.run(backup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print_success("Backup criado com sucesso!")
        else:
            print_warning(f"Erro no backup: {result.stderr.decode()}")
        
        # 2. Criar novo arquivo pg_hba.conf
        print_info("Criando novo arquivo de configuração...")
        
        new_config = """# PostgreSQL Client Authentication Configuration File
# ===================================================
#
# Refer to the "Client Authentication" section in the PostgreSQL
# documentation for a complete description of this file.

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5

# IPv6 local connections:
host    all             all             ::1/128                 md5

# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     md5
host    replication     all             127.0.0.1/32            md5
host    replication     all             ::1/128                 md5

# Configuração corrigida para autenticação por senha
host    all             all             0.0.0.0/0               md5
"""
        
        # 3. Criar arquivo temporário
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(new_config)
            temp_file_path = temp_file.name
        
        # 4. Copiar arquivo temporário para o local correto
        print_info("Aplicando nova configuração...")
        copy_cmd = ['sudo', '-u', 'postgres', 'cp', temp_file_path, config_file]
        result = subprocess.run(copy_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Limpar arquivo temporário
        os.unlink(temp_file_path)
        
        if result.returncode != 0:
            print_error(f"Erro ao aplicar configuração: {result.stderr.decode()}")
            return False
        
        print_success("Configuração aplicada com sucesso!")
        
        # 5. Reiniciar PostgreSQL
        print_info("Reiniciando PostgreSQL...")
        restart_commands = [
            ['sudo', 'systemctl', 'restart', 'postgresql'],
            ['sudo', 'systemctl', 'restart', 'postgresql.service'],
            ['sudo', 'service', 'postgresql', 'restart']
        ]
        
        restarted = False
        for cmd in restart_commands:
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    print_success("PostgreSQL reiniciado com sucesso!")
                    restarted = True
                    break
            except FileNotFoundError:
                continue
        
        if not restarted:
            print_warning("Não foi possível reiniciar automaticamente")
            print_info("Execute manualmente: sudo systemctl restart postgresql")
        
        # 6. Testar conexão
        print_info("Testando conexão...")
        test_cmd = ['sudo', '-u', 'postgres', 'psql', '-c', 'SELECT 1;']
        result = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            print_success("Conexão PostgreSQL testada com sucesso!")
        else:
            print_warning(f"Teste de conexão falhou: {result.stderr.decode()}")
        
        print_success("Correção concluída!")
        print_info("Agora você pode executar: python quick_setup.py setup")
        
        return True
        
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False

def main():
    """Função principal"""
    try:
        success = fix_postgresql_auth()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
