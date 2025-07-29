from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    nome = input('Nome do admin: ')
    username = input('Usuário admin: ')
    email = input('Email do admin: ')
    password = input('Senha: ')
    if User.query.filter_by(username=username).first():
        print('Usuário já existe.')
    else:
        user = User(
            username=username, 
            nome=nome, 
            email=email, 
            password=generate_password_hash(password), 
            status='ativo',
            role_id=1  # Perfil admin
        )
        db.session.add(user)
        db.session.commit()
        print('Usuário admin criado com sucesso!') 