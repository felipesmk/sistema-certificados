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
    system = platform.system().lower()
    
    try:
        import dotenv
        print("✅ Dependências básicas verificadas")
        
        # Verificar dependências específicas do sistema
        if system == 'windows':
            try:
                import waitress
                print("✅ Waitress (Windows) verificado")
            except ImportError:
                print("❌ Waitress não encontrado")
                print("Execute: pip install waitress")
                return False
        else:
            # Linux/Mac: verificar gunicorn
            try:
                import gunicorn
                print("✅ Gunicorn (Linux/Mac) verificado")
            except ImportError:
                print("❌ Gunicorn não encontrado")
                print("Execute: pip install gunicorn")
                print("Ou execute: pip install -r requirements.txt")
                return False
        
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
    except FileNotFoundError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        if system != 'windows':
            print("\n🔧 SOLUÇÃO:")
            print("1. Instale o gunicorn:")
            print("   pip install gunicorn")
            print("2. Ou reinstale todas as dependências:")
            print("   pip install -r requirements.txt")
            print("3. Tente novamente:")
            print("   python run_production.py")
        else:
            print("\n🔧 SOLUÇÃO:")
            print("1. Instale o waitress:")
            print("   pip install waitress")
            print("2. Ou reinstale todas as dependências:")
            print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("\n🔧 Verifique se o ambiente virtual está ativado e as dependências instaladas")
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