#!/usr/bin/env python3
"""
Script para testar as validações do sistema
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Responsavel
from utils.validation import (
    validate_email, check_email_exists, validate_name,
    validate_username, check_username_exists, validate_password,
    validate_phone, validate_registro_name, validate_future_date,
    validate_alert_time, validate_date
)

def test_validations():
    """Testa as validações do sistema"""
    
    with app.app_context():
        print("🧪 Testando validações do sistema...")
        
        # Teste 1: Validação de email válido
        print("\n1. Testando email válido:")
        is_valid, error = validate_email("teste@empresa.com")
        print(f"   Email: teste@empresa.com")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 2: Validação de email inválido
        print("\n2. Testando email inválido:")
        is_valid, error = validate_email("email_invalido")
        print(f"   Email: email_invalido")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 3: Validação de email vazio
        print("\n3. Testando email vazio:")
        is_valid, error = validate_email("")
        print(f"   Email: (vazio)")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 4: Validação de nome válido
        print("\n4. Testando nome válido:")
        is_valid, error = validate_name("João Silva", "Nome")
        print(f"   Nome: João Silva")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 5: Validação de nome muito curto
        print("\n5. Testando nome muito curto:")
        is_valid, error = validate_name("A", "Nome")
        print(f"   Nome: A")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 6: Verificar email existente no banco
        print("\n6. Verificando emails existentes no banco:")
        responsaveis = Responsavel.query.all()
        print(f"   Total de responsáveis: {len(responsaveis)}")
        
        for resp in responsaveis:
            print(f"   - {resp.nome}: {resp.email}")
        
        # Teste 7: Verificar se email específico existe
        if responsaveis:
            email_teste = responsaveis[0].email
            exists, msg = check_email_exists(email_teste, Responsavel)
            print(f"\n7. Verificando se '{email_teste}' existe:")
            print(f"   Existe: {exists}")
            print(f"   Mensagem: {msg}")
        
        # Teste 8: Validação de username
        print("\n8. Testando validação de username:")
        is_valid, error = validate_username("usuario_teste")
        print(f"   Username: usuario_teste")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 9: Validação de senha
        print("\n9. Testando validação de senha:")
        is_valid, error = validate_password("senha123")
        print(f"   Senha: senha123")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 10: Validação de telefone
        print("\n10. Testando validação de telefone:")
        is_valid, error = validate_phone("11987654321")
        print(f"   Telefone: 11987654321")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 11: Validação de nome de registro
        print("\n11. Testando validação de nome de registro:")
        is_valid, error = validate_registro_name("Certificado ISO 9001")
        print(f"   Nome: Certificado ISO 9001")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 12: Validação de data futura
        print("\n12. Testando validação de data futura:")
        from datetime import date, timedelta
        data_futura = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
        is_valid, error = validate_future_date(data_futura, "Data de vencimento")
        print(f"   Data: {data_futura}")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 13: Validação de tempo de alerta
        print("\n13. Testando validação de tempo de alerta:")
        is_valid, error = validate_alert_time("30")
        print(f"   Tempo: 30")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        # Teste 14: Validação de data inválida
        print("\n14. Testando data inválida:")
        is_valid, error = validate_date("data_invalida", "Data")
        print(f"   Data: data_invalida")
        print(f"   Válido: {is_valid}")
        print(f"   Erro: {error}")
        
        print("\n✅ Testes concluídos!")

if __name__ == '__main__':
    test_validations()
