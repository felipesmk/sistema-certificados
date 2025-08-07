#!/usr/bin/env python3
"""
Script para instalar dependências de produção automaticamente.
Este script detecta o sistema operacional e instala as dependências necessárias.
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """Instala as dependências de produção"""
    system = platform.system().lower()
    
    print("🔧 Instalando dependências de produção...")
    print(f"📋 Sistema detectado: {system}")
    print()
    
    try:
        # Instalar dependências básicas
        print("📦 Instalando dependências do requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências básicas instaladas")
        
        # Verificar dependências específicas
        if system == 'windows':
            try:
                import waitress
                print("✅ Waitress já está instalado")
            except ImportError:
                print("📦 Instalando Waitress...")
                subprocess.run([sys.executable, "-m", "pip", "install", "waitress"], check=True)
                print("✅ Waitress instalado")
        else:
            try:
                import gunicorn
                print("✅ Gunicorn já está instalado")
            except ImportError:
                print("📦 Instalando Gunicorn...")
                subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
                print("✅ Gunicorn instalado")
        
        print()
        print("🎉 Todas as dependências foram instaladas com sucesso!")
        print()
        print("🚀 Agora você pode executar:")
        print("   python run_production.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("\n🔧 Tente executar manualmente:")
        print("   pip install -r requirements.txt")
        if system != 'windows':
            print("   pip install gunicorn")
        else:
            print("   pip install waitress")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    print("🏭 Sistema de Certificados - Instalador de Dependências")
    print("=" * 60)
    print()
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("requirements.txt"):
        print("❌ Arquivo requirements.txt não encontrado!")
        print("   Certifique-se de estar no diretório do projeto")
        sys.exit(1)
    
    # Instalar dependências
    install_dependencies()

if __name__ == '__main__':
    main()
