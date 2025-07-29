#!/usr/bin/env python3
"""
Script para executar a aplicação em produção usando Waitress (Windows) ou Gunicorn (Linux).
Este script configura o ambiente e inicia o servidor.
"""

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path

def setup_environment():
    """Configura o ambiente para produção"""
    # Definir variáveis de ambiente para produção
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    # Criar diretório de logs se não existir
    Path('logs').mkdir(exist_ok=True)
    
    print("✅ Ambiente de produção configurado")

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import dotenv
        print("✅ Dependências de produção verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def start_server():
    """Inicia o servidor baseado no sistema operacional"""
    system = platform.system().lower()
    
    try:
        if system == 'windows':
            # Windows: usar Waitress
            print("🪟 Detectado Windows - usando Waitress")
            cmd = [
                'waitress-serve',
                '--host', '0.0.0.0',
                '--port', '8000',
                'app:app'
            ]
        else:
            # Linux/Mac: usar Gunicorn
            print("🐧 Detectado Linux/Mac - usando Gunicorn")
            cmd = [
                'gunicorn',
                '--config', 'gunicorn.conf.py',
                '--bind', '0.0.0.0:8000',
                '--workers', '4',
                '--timeout', '30',
                '--access-logfile', 'logs/gunicorn_access.log',
                '--error-logfile', 'logs/gunicorn_error.log',
                'app:app'
            ]
        
        print("🚀 Iniciando servidor...")
        print(f"📝 Comando: {' '.join(cmd)}")
        print("🌐 Aplicação disponível em: http://localhost:8000")
        print("📊 Logs em: logs/")
        print("⏹️  Para parar: Ctrl+C")
        
        # Executar o comando
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🏭 Sistema de Certificados - Modo Produção")
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