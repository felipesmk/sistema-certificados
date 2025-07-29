# init_db.py
"""
Script para inicializar o banco de dados, criar permissões e o perfil admin com todas as permissões.
Pode ser executado sempre que precisar resetar o banco.
"""
import os
from app import db, app
from models import Role, Permission, RolePermission

# Caminho correto do banco considerando a pasta instance
DB_PATH = os.path.join(app.instance_path, 'certificados.db')

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print('Banco de dados removido.')
else:
    print('Banco de dados não existia.')

with app.app_context():
    db.create_all()
    print('Tabelas criadas com sucesso!')

    # Permissões padrão do sistema
    permissoes = [
        'manage_access',      # Gerenciar usuários e perfis
        'manage_registros',   # Gerenciar registros
        'manage_responsaveis',# Gerenciar responsáveis
        'manage_config',      # Gerenciar configurações
        'send_alerts'         # Enviar alertas por email
    ]
    perm_objs = []
    for perm_nome in permissoes:
        perm = Permission.query.filter_by(nome=perm_nome).first()
        if not perm:
            perm = Permission(nome=perm_nome, descricao=f'Permissão para {perm_nome}')
            db.session.add(perm)
        perm_objs.append(perm)
    db.session.commit()

    # Cria ou obtém o perfil admin
    admin_role = Role.query.filter_by(nome='admin').first()
    if not admin_role:
        admin_role = Role(nome='admin', descricao='Administrador do sistema')
        db.session.add(admin_role)
        db.session.commit()

    # Cria ou obtém o perfil operador
    operador_role = Role.query.filter_by(nome='operador').first()
    if not operador_role:
        operador_role = Role(nome='operador', descricao='Operador do sistema - pode gerenciar registros, responsáveis e enviar alertas')
        db.session.add(operador_role)
        db.session.commit()

    # Cria ou obtém o perfil visualizador
    visualizador_role = Role.query.filter_by(nome='visualizador').first()
    if not visualizador_role:
        visualizador_role = Role(nome='visualizador', descricao='Visualizador - apenas visualização de dados')
        db.session.add(visualizador_role)
        db.session.commit()

    # Associa todas as permissões ao perfil admin (evita duplicatas)
    for perm in perm_objs:
        if not RolePermission.query.filter_by(role_id=admin_role.id, permission_id=perm.id).first():
            db.session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))
    db.session.commit()

    # Associa permissões ao perfil operador
    operador_perms = ['manage_registros', 'manage_responsaveis', 'send_alerts']
    for perm_nome in operador_perms:
        perm = Permission.query.filter_by(nome=perm_nome).first()
        if perm and not RolePermission.query.filter_by(role_id=operador_role.id, permission_id=perm.id).first():
            db.session.add(RolePermission(role_id=operador_role.id, permission_id=perm.id))
    db.session.commit()

    # Visualizador não tem permissões específicas (apenas visualização)
    
    print('Perfis e permissões criados com sucesso!')
    print(f'- Admin: {admin_role.nome} (todas as permissões)')
    print(f'- Operador: {operador_role.nome} (registros, responsáveis, alertas)')
    print(f'- Visualizador: {visualizador_role.nome} (apenas visualização)') 