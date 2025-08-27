#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar a aplicação em produção usando Waitress (Windows) ou Gunicorn (Linux).
Este script configura o ambiente e inicia o servidor.
"""

import os
import sys
import subprocess
import platform
import socket
from pathlib import Path

def setup_environment():
    """Configura o ambiente para produção"""
    # Definir variáveis de ambiente para produção
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    # Criar diretório de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    print("Ambiente de produção configurado")

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    system = platform.system().lower()
    
    try:
        import dotenv
        print("Dependências básicas verificadas")
        
        # Verificar dependências específicas do sistema
        if system == 'windows':
            try:
                import waitress
                print("Waitress (Windows) verificado")
            except ImportError:
                print("Waitress não encontrado")
                print("Execute: pip install waitress")
                return False
        else:
            # Linux/Mac: verificar gunicorn
            try:
                import gunicorn
                print("Gunicorn (Linux/Mac) verificado")
            except ImportError:
                print("Gunicorn não encontrado")
                print("Execute: pip install gunicorn")
                print("Ou execute: pip install -r requirements.txt")
                return False
        
        print("Dependências de produção verificadas")
        return True
    except ImportError as e:
        print("Dependência faltando: {}".format(e))
        print("Execute: pip install -r requirements.txt")
        return False

def detect_machine_ip() -> str:
    """Tenta detectar o IP local não-loopback para binding externo."""
    # Tentativa via socket conectado (não envia tráfego)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip_addr = sock.getsockname()[0]
        sock.close()
        if ip_addr and ip_addr != "127.0.0.1":
            return ip_addr
    except Exception:
        pass

    # Fallback para hostname
    try:
        ip_addr = socket.gethostbyname(socket.gethostname())
        if ip_addr:
            return ip_addr
    except Exception:
        pass

    # Último recurso
    return "0.0.0.0"

def start_server():
    """Inicia o servidor baseado no sistema operacional"""
    system = platform.system().lower()
    ip_addr = detect_machine_ip()
    port = 80  # Porta HTTP padrão para evitar :80 na URL
    
    try:
        if system == 'windows':
            # Windows: usar Waitress
            print("Detectado Windows - usando Waitress")
            cmd = [
                'waitress-serve',
                '--host', ip_addr,
                '--port', str(port),
                'app:app'
            ]
        else:
            # Linux/Mac: usar Gunicorn
            print("Detectado Linux/Mac - usando Gunicorn")
            # Aviso para portas privilegiadas (<1024)
            if hasattr(os, 'geteuid') and os.geteuid() != 0 and port < 1024:
                print("Aviso: ligar na porta 80 em Linux requer privilégios elevados.")
                print("Opções:")
                print(" - Executar com sudo: sudo python run_production.py")
                print(" - OU conceder capacidade: sudo setcap 'cap_net_bind_service=+ep' $(command -v gunicorn)")
            cmd = [
                'gunicorn',
                '--config', 'gunicorn.conf.py',
                '--bind', '{}:{}'.format(ip_addr, port),
                '--workers', '4',
                '--timeout', '30',
                '--access-logfile', 'logs/gunicorn_access.log',
                '--error-logfile', 'logs/gunicorn_error.log',
                'app:app'
            ]
        
        print("Iniciando servidor...")
        print("Comando: {}".format(' '.join(cmd)))
        # Mostrar URL padrão sem :80
        if ip_addr in ("0.0.0.0", "127.0.0.1"):
            print("Aplicação disponível em: http://localhost")
        else:
            print("Aplicação disponível em: http://{}".format(ip_addr))
        print("Logs em: logs/")
        print("Para parar: Ctrl+C")
        
        # Executar o comando
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\nServidor parado pelo usuário")
    except FileNotFoundError as e:
        print("Erro ao iniciar servidor: {}".format(e))
        if system != 'windows':
            print("\nSolução:")
            print("1. Instale o gunicorn:")
            print("   pip install gunicorn")
            print("2. Ou reinstale todas as dependências:")
            print("   pip install -r requirements.txt")
            print("3. Tente novamente:")
            print("   python run_production.py")
        else:
            print("\nSolução:")
            print("1. Instale o waitress:")
            print("   pip install waitress")
            print("2. Ou reinstale todas as dependências:")
            print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print("Erro ao iniciar servidor: {}".format(e))
        print("\nVerifique se o ambiente virtual está ativado e as dependências instaladas")
        sys.exit(1)

def main():
    """Função principal"""
    print("Sistema de Certificados - Modo Produção")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    # Iniciar servidor
    start_server()

if __name__ == '__main__':
    main() 