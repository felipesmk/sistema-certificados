# -*- coding: utf-8 -*-
"""
Utilitários de validação para o sistema
"""

import re
from typing import Tuple, List, Optional
from models import User, Responsavel

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email e verifica se já existe no sistema.
    
    Args:
        email: Email a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not email or not email.strip():
        return False, "E-mail é obrigatório"
    
    email = email.strip().lower()
    
    # Validar formato
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Formato de e-mail inválido"
    
    return True, ""

def check_email_exists(email: str, model_class, exclude_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Verifica se um email já existe no banco de dados.
    
    Args:
        email: Email a ser verificado
        model_class: Classe do modelo (User ou Responsavel)
        exclude_id: ID a ser excluído da verificação (para edição)
        
    Returns:
        Tuple[bool, str]: (existe, mensagem)
    """
    email = email.strip().lower()
    
    query = model_class.query.filter_by(email=email)
    if exclude_id:
        query = query.filter(model_class.id != exclude_id)
    
    existing_record = query.first()
    
    if existing_record:
        if model_class == User:
            return True, f"E-mail já está em uso pelo usuário '{existing_record.nome}'"
        elif model_class == Responsavel:
            return True, f"E-mail já está cadastrado para o responsável '{existing_record.nome}'"
        else:
            return True, "E-mail já está em uso"
    
    return False, ""

def validate_username(username: str) -> Tuple[bool, str]:
    """
    Valida nome de usuário.
    
    Args:
        username: Nome de usuário a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not username or not username.strip():
        return False, "Nome de usuário é obrigatório"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Nome de usuário deve ter pelo menos 3 caracteres"
    
    if len(username) > 80:
        return False, "Nome de usuário deve ter no máximo 80 caracteres"
    
    # Validar caracteres permitidos
    username_pattern = r'^[a-zA-Z0-9._-]+$'
    if not re.match(username_pattern, username):
        return False, "Nome de usuário deve conter apenas letras, números, pontos, hífens e underscores"
    
    return True, ""

def check_username_exists(username: str, exclude_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Verifica se um nome de usuário já existe.
    
    Args:
        username: Nome de usuário a ser verificado
        exclude_id: ID a ser excluído da verificação (para edição)
        
    Returns:
        Tuple[bool, str]: (existe, mensagem)
    """
    username = username.strip().lower()
    
    query = User.query.filter_by(username=username)
    if exclude_id:
        query = query.filter(User.id != exclude_id)
    
    existing_user = query.first()
    
    if existing_user:
        return True, f"Nome de usuário já existe"
    
    return False, ""

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valida senha.
    
    Args:
        password: Senha a ser validada
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not password:
        return False, "Senha é obrigatória"
    
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    
    if len(password) > 200:
        return False, "Senha deve ter no máximo 200 caracteres"
    
    return True, ""

def validate_name(name: str, field_name: str = "Nome") -> Tuple[bool, str]:
    """
    Valida nome genérico.
    
    Args:
        name: Nome a ser validado
        field_name: Nome do campo para mensagens de erro
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not name or not name.strip():
        return False, f"{field_name} é obrigatório"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, f"{field_name} deve ter pelo menos 2 caracteres"
    
    if len(name) > 120:
        return False, f"{field_name} deve ter no máximo 120 caracteres"
    
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Valida número de telefone.
    
    Args:
        phone: Telefone a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not phone:
        return True, ""  # Telefone é opcional
    
    phone = re.sub(r'[^\d]', '', phone)  # Remove caracteres não numéricos
    
    if len(phone) < 8:
        return False, "Telefone deve ter pelo menos 8 dígitos"
    
    if len(phone) > 15:
        return False, "Telefone deve ter no máximo 15 dígitos"
    
    return True, ""

def validate_registro_name(name: str) -> Tuple[bool, str]:
    """
    Valida nome do registro.
    
    Args:
        name: Nome do registro a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not name or not name.strip():
        return False, "Nome do registro é obrigatório"
    
    name = name.strip()
    
    if len(name) < 3:
        return False, "Nome do registro deve ter pelo menos 3 caracteres"
    
    if len(name) > 200:
        return False, "Nome do registro deve ter no máximo 200 caracteres"
    
    return True, ""

def validate_date(date_str: str, field_name: str = "Data") -> Tuple[bool, str]:
    """
    Valida formato de data.
    
    Args:
        date_str: String da data a ser validada
        field_name: Nome do campo para mensagens de erro
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not date_str or not date_str.strip():
        return False, f"{field_name} é obrigatória"
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, f"{field_name} deve estar no formato AAAA-MM-DD"

def validate_future_date(date_str: str, field_name: str = "Data de vencimento") -> Tuple[bool, str]:
    """
    Valida se a data é futura.
    
    Args:
        date_str: String da data a ser validada
        field_name: Nome do campo para mensagens de erro
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    is_valid, error_msg = validate_date(date_str, field_name)
    if not is_valid:
        return False, error_msg
    
    try:
        from datetime import datetime, date
        data_vencimento = datetime.strptime(date_str, '%Y-%m-%d').date()
        hoje = date.today()
        
        if data_vencimento <= hoje:
            return False, f"{field_name} deve ser uma data futura"
        
        return True, ""
    except ValueError:
        return False, f"{field_name} deve estar no formato AAAA-MM-DD"

def validate_alert_time(tempo_alerta: str) -> Tuple[bool, str]:
    """
    Valida tempo de alerta.
    
    Args:
        tempo_alerta: Tempo de alerta a ser validado
        
    Returns:
        Tuple[bool, str]: (é_válido, mensagem_erro)
    """
    if not tempo_alerta:
        return False, "Tempo de alerta é obrigatório"
    
    try:
        tempo = int(tempo_alerta)
        if tempo < 1:
            return False, "Tempo de alerta deve ser pelo menos 1 dia"
        if tempo > 365:
            return False, "Tempo de alerta deve ser no máximo 365 dias"
        return True, ""
    except ValueError:
        return False, "Tempo de alerta deve ser um número inteiro"

def format_validation_errors(errors: List[str]) -> str:
    """
    Formata lista de erros de validação para exibição.
    
    Args:
        errors: Lista de mensagens de erro
        
    Returns:
        str: Erros formatados
    """
    if not errors:
        return ""
    
    if len(errors) == 1:
        return errors[0]
    
    return "• " + "\n• ".join(errors)
