#!/usr/bin/env python3
"""
SETUP RÁPIDO DO SISTEMA
========================

Script para configuração rápida do sistema de certificados.
Executa as operações mais comuns de forma automatizada.

Uso: python quick_setup.py [opção]
"""

import sys
import os
import subprocess
import platform

def run_command(command, description, interactive=False):
    """Executa comando e mostra resultado"""
    print(f"\n[RUN] {description}...")
    print(f"[CMD] {command}")
    try:
        if interactive:
            # Para comandos interativos, usar subprocess.run sem capturar saída
            return_code = subprocess.run(command, shell=True).returncode
            if return_code == 0:
                print(f"\n[OK] {description} - Concluído!")
            else:
                print(f"\n[ERROR] {description} - Erro! (código: {return_code})")
            return return_code == 0
        else:
            # Usar Popen para mostrar saída em tempo real (não interativo)
            process = subprocess.Popen(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Mostrar saída em tempo real
            output_lines = []
            for line in process.stdout:
                print(line.rstrip())
                output_lines.append(line)
            
            # Aguardar conclusão
            return_code = process.wait()
            
            if return_code == 0:
                print(f"\n[OK] {description} - Concluído!")
            else:
                print(f"\n[ERROR] {description} - Erro! (código: {return_code})")
                
            return return_code == 0
        
    except Exception as e:
        print(f"[ERROR] Erro ao executar: {e}")
        return False

def setup_new_system():
    """Configuração completa de um sistema novo"""
    print("CONFIGURAÇÃO COMPLETA DO SISTEMA")
    print("="*50)
    
    steps = [
        ("python manage_db.py reset --force", "Resetando banco de dados"),
        ("python manage_db.py migrate", "Executando migrações (incluindo campos avançados de usuários)"),
        ("python manage_db.py backup", "Criando backup inicial"),
        ("python manage_db.py status", "Verificando status final")
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n[ERROR] Falha na etapa: {description}")
            return False
    
    # Criar admin de forma interativa
    print("\n" + "="*50)
    print("CRIAÇÃO DO USUÁRIO ADMINISTRADOR")
    print("="*50)
    print("Agora vamos criar o usuário administrador do sistema.")
    print("Você pode usar os valores padrão pressionando Enter.")
    
    if not run_command("python manage_db.py create-admin", "Criando usuário administrador", interactive=True):
        print(f"\n[ERROR] Falha ao criar usuário administrador")
        return False
    
    print("\n[SUCCESS] SISTEMA CONFIGURADO COM SUCESSO!")
    print("Próximos passos:")
    print("   1. Execute: python app.py")
    print("   2. Acesse: http://localhost:5000")
    print("   3. Faça login com as credenciais que você criou")
    return True

def quick_start():
    """Início rápido sem reset"""
    print("INÍCIO RÁPIDO")
    print("="*30)
    
    steps = [
        ("python manage_db.py status", "Verificando banco de dados"),
        ("python manage_db.py migrate", "Aplicando migrações"),
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n[ERROR] Falha na etapa: {description}")
            return False
    
    print("\n[SUCCESS] SISTEMA PRONTO!")
    print("Para iniciar:")
    print("   python app.py")
    return True

def create_demo_users():
    """Cria usuários de demonstração"""
    print("CRIANDO USUÁRIOS DE DEMONSTRAÇÃO")
    print("="*40)
    
    demo_users = [
        ("operador1", "João Operador", "joao@empresa.com", "123456", "operador"),
        ("visual1", "Maria Visualizadora", "maria@empresa.com", "123456", "visualizador"),
        ("gestor1", "Pedro Gestor", "pedro@empresa.com", "123456", "operador")
    ]
    
    for username, name, email, password, role in demo_users:
        command = f'python manage_db.py create-user {username} "{name}" {email} {password} {role}'
        run_command(command, f"Criando usuário {username}")
    
    print("\n[SUCCESS] USUÁRIOS DE DEMO CRIADOS!")
    print("Usuários disponíveis:")
    for username, name, email, password, role in demo_users:
        print(f"   {username} / {password} ({role})")

def install_production_deps():
    """Instala dependências de produção"""
    print("INSTALAÇÃO DE DEPENDÊNCIAS DE PRODUÇÃO")
    print("="*50)
    
    system = platform.system().lower()
    print(f"📋 Sistema detectado: {system}")
    print()
    
    try:
        # Instalar dependências básicas
        print("📦 Instalando dependências do requirements.txt...")
        if not run_command("pip install -r requirements.txt", "Instalando dependências básicas"):
            return False
        
        # Verificar dependências específicas
        if system == 'windows':
            try:
                import waitress
                print("✅ Waitress já está instalado")
            except ImportError:
                print("📦 Instalando Waitress...")
                if not run_command("pip install waitress", "Instalando Waitress"):
                    return False
        else:
            try:
                import gunicorn
                print("✅ Gunicorn já está instalado")
            except ImportError:
                print("📦 Instalando Gunicorn...")
                if not run_command("pip install gunicorn", "Instalando Gunicorn"):
                    return False
        
        print("\n[SUCCESS] Todas as dependências foram instaladas com sucesso!")
        print("🚀 Agora você pode executar:")
        print("   python run_production.py")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro inesperado: {e}")
        return False

def backup_system():
    """Cria backup completo do sistema"""
    print("BACKUP DO SISTEMA")
    print("="*25)
    
    if run_command("python manage_db.py backup", "Criando backup do banco"):
        print("\n[SUCCESS] Backup criado com sucesso!")
        print("Localização: pasta 'backups/'")
    else:
        print("\n[ERROR] Falha ao criar backup!")

def test_user_features():
    """Testa funcionalidades avançadas de usuários"""
    print("TESTE DAS FUNCIONALIDADES DE USUÁRIOS")
    print("="*40)
    
    steps = [
        ("python manage_db.py migrate", "Aplicando migrações de usuários"),
        ("python manage_db.py status", "Verificando campos avançados"),
        ("python manage_db.py create-user testuser \"Usuário Teste\" test@empresa.com 123456 operador", "Criando usuário de teste")
    ]
    
    for command, description in steps:
        if not run_command(command, description):
            print(f"\n[ERROR] Falha na etapa: {description}")
            return False
    
    print("\n[SUCCESS] FUNCIONALIDADES DE USUÁRIOS TESTADAS!")
    print("Agora você pode:")
    print("   1. Fazer login com 'testuser' / '123456'")
    print("   2. Testar o dashboard de usuários")
    print("   3. Verificar os novos campos no formulário")
    return True

def show_menu():
    """Mostra menu principal"""
    print("\n" + "="*60)
    print("SETUP RÁPIDO DO SISTEMA DE CERTIFICADOS")
    print("="*60)
    print()
    print("Escolha uma opção:")
    print()
    print("1. Setup Completo (reset + admin + migrações)")
    print("2. Início Rápido (apenas migrações)")
    print("3. Criar Usuários de Demo")
    print("4. Testar Funcionalidades de Usuários")
    print("5. Instalar Dependências de Produção")
    print("6. Backup do Sistema")
    print("7. Status do Sistema")
    print("8. Sair")
    print()

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        option = sys.argv[1]
        if option == "setup":
            setup_new_system()
        elif option == "start":
            quick_start()
        elif option == "demo":
            create_demo_users()
        elif option == "backup":
            backup_system()
        elif option == "test-users":
            test_user_features()
        elif option == "install-prod":
            install_production_deps()
        elif option == "status":
            run_command("python manage_db.py status", "Verificando status")
        else:
            print(f"[ERROR] Opção inválida: {option}")
            print("Opções: setup, start, demo, backup, test-users, install-prod, status")
        return
    
    # Menu interativo
    while True:
        show_menu()
        
        try:
            choice = input("Digite sua escolha (1-7): ").strip()
            
            if choice == "1":
                if input("\n[WARN] Isto irá RESETAR o banco! Confirma? (s/N): ").lower() == 's':
                    setup_new_system()
                else:
                    print("Operação cancelada.")
                    
            elif choice == "2":
                quick_start()
                
            elif choice == "3":
                create_demo_users()
                
            elif choice == "4":
                test_user_features()
                
            elif choice == "5":
                install_production_deps()
                
            elif choice == "6":
                backup_system()
                
            elif choice == "7":
                run_command("python manage_db.py status", "Verificando status")
                
            elif choice == "8":
                print("\nAté logo!")
                break
                
            else:
                print("\n[ERROR] Opção inválida! Escolha entre 1-8.")
                
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                input("\nPressione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\nSaindo...")
            break
        except Exception as e:
            print(f"\n[ERROR] Erro: {e}")

if __name__ == "__main__":
    main()