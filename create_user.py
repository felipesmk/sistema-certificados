#!/usr/bin/env python3
"""
Script para criar usuários com diferentes perfis.
Permite criar usuários admin, operador ou visualizador.
"""

from app import app, db
from models import User, Role
from werkzeug.security import generate_password_hash

def listar_perfis():
    """Lista todos os perfis disponíveis"""
    perfis = Role.query.all()
    print("\nPerfis disponíveis:")
    for i, perfil in enumerate(perfis, 1):
        print(f"{i}. {perfil.nome} - {perfil.descricao}")
    return perfis

def criar_usuario():
    """Cria um novo usuário"""
    print("=== Criar Novo Usuário ===")
    
    # Listar perfis
    perfis = listar_perfis()
    
    # Coletar dados do usuário
    username = input('\nNome de usuário: ').strip()
    if not username:
        print("Nome de usuário é obrigatório!")
        return
    
    # Verificar se usuário já existe
    if User.query.filter_by(username=username).first():
        print(f"Usuário '{username}' já existe!")
        return
    
    nome = input('Nome completo: ').strip()
    if not nome:
        print("Nome completo é obrigatório!")
        return
    
    email = input('Email: ').strip()
    if not email:
        print("Email é obrigatório!")
        return
    
    password = input('Senha: ').strip()
    if not password:
        print("Senha é obrigatória!")
        return
    
    # Selecionar perfil
    try:
        perfil_escolha = int(input(f'\nEscolha o perfil (1-{len(perfis)}): '))
        if perfil_escolha < 1 or perfil_escolha > len(perfis):
            print("Opção inválida!")
            return
        perfil = perfis[perfil_escolha - 1]
    except ValueError:
        print("Opção inválida!")
        return
    
    # Criar usuário
    try:
        user = User(
            username=username,
            nome=nome,
            email=email,
            password=generate_password_hash(password),
            status='ativo',
            role_id=perfil.id
        )
        db.session.add(user)
        db.session.commit()
        print(f"\n✅ Usuário '{username}' criado com sucesso!")
        print(f"   Perfil: {perfil.nome}")
        print(f"   Email: {email}")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        db.session.rollback()

def main():
    """Função principal"""
    print("🏭 Sistema de Certificados - Criador de Usuários")
    print("=" * 50)
    
    with app.app_context():
        while True:
            print("\nOpções:")
            print("1. Criar novo usuário")
            print("2. Listar perfis")
            print("3. Sair")
            
            opcao = input("\nEscolha uma opção (1-3): ").strip()
            
            if opcao == '1':
                criar_usuario()
            elif opcao == '2':
                listar_perfis()
            elif opcao == '3':
                print("Saindo...")
                break
            else:
                print("Opção inválida!")

if __name__ == '__main__':
    main() 