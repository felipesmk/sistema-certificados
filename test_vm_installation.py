#!/usr/bin/env python3
"""
Script de Teste para Validação da Instalação na VM
"""

import os
import sys
import subprocess
import requests
import sqlite3
from datetime import datetime

# Imports para PostgreSQL (opcionais)
try:
    from sqlalchemy import text, inspect
except ImportError:
    text = None
    inspect = None

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    """Imprime passo do teste"""
    print(f"\n[{step}] {description}")
    print("-" * 40)

def run_command(command, capture_output=True):
    """Executa comando e retorna resultado"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def test_python_environment():
    """Testa ambiente Python"""
    print_step("1", "Testando Ambiente Python")
    
    # Verificar versão Python
    success, output, error = run_command("python --version")
    if success:
        print(f"✅ Python: {output.strip()}")
    else:
        print(f"❌ Python não encontrado: {error}")
        return False
    
    # Verificar pip
    success, output, error = run_command("pip --version")
    if success:
        print(f"✅ Pip: {output.strip()}")
    else:
        print(f"❌ Pip não encontrado: {error}")
        return False
    
    # Verificar ambiente virtual
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Ambiente virtual ativo")
    else:
        print("⚠️  Ambiente virtual não detectado")
    
    return True

def test_dependencies():
    """Testa dependências instaladas"""
    print_step("2", "Testando Dependências")
    
    required_packages = [
        'flask', 'sqlalchemy', 'flask-login', 'flask-principal',
        'ldap3', 'python-dotenv', 'werkzeug'
    ]
    
    all_installed = True
    for package in required_packages:
        success, output, error = run_command(f"python -c \"import {package}\"")
        if success:
            print(f"✅ {package}")
        else:
            print(f"❌ {package}: {error}")
            all_installed = False
    
    return all_installed

def test_database():
    """Testa banco de dados"""
    print_step("3", "Testando Banco de Dados")
    
    # Detectar tipo de banco
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL não encontrada no ambiente!")
        print("Execute: python configure_postgresql.py")
        return False
    
    if db_url.startswith('postgresql://'):
        print("🔍 Detectado PostgreSQL")
        return test_postgresql_database()
    else:
        print("🔍 Detectado SQLite")
        return test_sqlite_database()

def test_postgresql_database():
    """Testa banco PostgreSQL"""
    try:
        # Importar dependências necessárias
        from app import app, db
        from models import User, Role, Permission
        
        with app.app_context():
            # Testar conexão
            db.session.execute(text("SELECT 1"))
            print("✅ Conexão PostgreSQL: OK")
            
            # Verificar tabelas
            inspector = inspect(db.engine)
            required_tables = ['user', 'role', 'permission', 'user_history', 'role_history']
            existing_tables = inspector.get_table_names()
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if not missing_tables:
                print("✅ Todas as tabelas necessárias encontradas")
            else:
                print(f"❌ Tabelas faltando: {missing_tables}")
                return False
            
            # Verificar usuários
            user_count = User.query.count()
            print(f"✅ Usuários no banco: {user_count}")
            
            # Verificar admin
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✅ Usuário admin encontrado")
            else:
                print("❌ Usuário admin não encontrado")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao conectar no PostgreSQL: {e}")
        return False

def test_sqlite_database():
    """Testa banco SQLite (legado)"""
    # Verificar se arquivo existe
    if os.path.exists("instance/app.db"):
        print("✅ Arquivo do banco encontrado")
        
        # Testar conexão
        try:
            conn = sqlite3.connect("instance/app.db")
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['user', 'role', 'permission', 'user_history', 'role_history']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if not missing_tables:
                print("✅ Todas as tabelas necessárias encontradas")
            else:
                print(f"❌ Tabelas faltando: {missing_tables}")
                return False
            
            # Verificar usuários
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]
            print(f"✅ Usuários no banco: {user_count}")
            
            # Verificar admin
            cursor.execute("SELECT username FROM user WHERE username='admin'")
            admin = cursor.fetchone()
            if admin:
                print("✅ Usuário admin encontrado")
            else:
                print("❌ Usuário admin não encontrado")
                return False
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao conectar no banco: {e}")
            return False
    else:
        print("❌ Arquivo do banco não encontrado")
        return False

def test_application_files():
    """Testa arquivos da aplicação"""
    print_step("4", "Testando Arquivos da Aplicação")
    
    required_files = [
        'app.py', 'models.py', 'requirements.txt',
        'manage_db.py', 'quick_setup.py'
    ]
    
    all_files_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_files_exist = False
    
    # Verificar diretórios
    required_dirs = ['templates', 'routes', 'utils', 'logs']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")
            all_files_exist = False
    
    return all_files_exist

def test_web_application():
    """Testa aplicação web"""
    print_step("5", "Testando Aplicação Web")
    
    # Verificar se aplicação está rodando
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Aplicação web respondendo")
            return True
        else:
            print(f"⚠️  Aplicação retornou status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Aplicação não está rodando (normal se não foi iniciada)")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar aplicação: {e}")
        return False

def test_network():
    """Testa configuração de rede"""
    print_step("6", "Testando Configuração de Rede")
    
    # Verificar IP
    if os.name == 'nt':  # Windows
        success, output, error = run_command("ipconfig | findstr IPv4")
    else:  # Linux
        success, output, error = run_command("hostname -I")
    
    if success and output.strip():
        print(f"✅ IP da VM: {output.strip()}")
    else:
        print("⚠️  Não foi possível obter IP")
    
    # Verificar porta 5000
    if os.name == 'nt':
        success, output, error = run_command("netstat -ano | findstr :5000")
    else:
        success, output, error = run_command("lsof -i :5000")
    
    if success and output.strip():
        print("✅ Porta 5000 está em uso")
    else:
        print("⚠️  Porta 5000 não está em uso")
    
    return True

def test_scripts():
    """Testa scripts de gerenciamento"""
    print_step("7", "Testando Scripts de Gerenciamento")
    
    # Testar manage_db.py status
    success, output, error = run_command("python manage_db.py status")
    if success:
        print("✅ manage_db.py status funcionando")
    else:
        print(f"❌ manage_db.py status falhou: {error}")
        return False
    
    # Testar quick_setup.py
    success, output, error = run_command("python quick_setup.py --help")
    if success:
        print("✅ quick_setup.py funcionando")
    else:
        print(f"❌ quick_setup.py falhou: {error}")
        return False
    
    return True

def generate_report(results):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Total de testes: {total_tests}")
    print(f"   ✅ Aprovados: {passed_tests}")
    print(f"   ❌ Falharam: {failed_tests}")
    print(f"   📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("   A VM está pronta para uso.")
    else:
        print(f"\n⚠️  {failed_tests} TESTE(S) FALHARAM:")
        for test_name, result in results.items():
            if not result:
                print(f"   - {test_name}")
        
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   1. Verificar erros específicos acima")
        print("   2. Executar setup_vm.bat novamente")
        print("   3. Verificar logs em logs/app.log")
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"vm_test_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Relatório de Teste da VM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total de testes: {total_tests}\n")
        f.write(f"Aprovados: {passed_tests}\n")
        f.write(f"Falharam: {failed_tests}\n")
        f.write(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%\n\n")
        
        for test_name, result in results.items():
            f.write(f"{'✅' if result else '❌'} {test_name}\n")
    
    print(f"\n📄 Relatório salvo em: {report_file}")

def main():
    """Função principal"""
    print_header("TESTE DE VALIDAÇÃO DA VM")
    print("Este script testa se a instalação na VM está correta.")
    
    # Lista de testes
    tests = [
        ("Ambiente Python", test_python_environment),
        ("Dependências", test_dependencies),
        ("Banco de Dados", test_database),
        ("Arquivos da Aplicação", test_application_files),
        ("Aplicação Web", test_web_application),
        ("Configuração de Rede", test_network),
        ("Scripts de Gerenciamento", test_scripts)
    ]
    
    results = {}
    
    # Executar testes
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results[test_name] = False
    
    # Gerar relatório
    generate_report(results)

if __name__ == "__main__":
    main() 