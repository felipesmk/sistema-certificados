# utils/pagination.py
"""Utilitários para paginação de resultados."""

from flask import request, url_for

def paginate_query(query, page=1, per_page=20):
    """Aplica paginação a uma query SQLAlchemy."""
    return query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )

def get_pagination_info(pagination, endpoint, **kwargs):
    """Gera informações de paginação para templates."""
    pages = []
    
    # Páginas anteriores
    if pagination.has_prev:
        pages.append({
            'number': pagination.prev_num,
            'url': url_for(endpoint, page=pagination.prev_num, **kwargs),
            'label': 'Anterior',
            'active': False
        })
    
    # Páginas numeradas
    for page_num in pagination.iter_pages(left_edge=2, left_current=2, right_current=3, right_edge=2):
        if page_num is None:
            pages.append({'number': None, 'url': None, 'label': '...', 'active': False})
        else:
            pages.append({
                'number': page_num,
                'url': url_for(endpoint, page=page_num, **kwargs),
                'label': str(page_num),
                'active': page_num == pagination.page
            })
    
    # Próxima página
    if pagination.has_next:
        pages.append({
            'number': pagination.next_num,
            'url': url_for(endpoint, page=pagination.next_num, **kwargs),
            'label': 'Próxima',
            'active': False
        })
    
    return {
        'pages': pages,
        'current_page': pagination.page,
        'total_pages': pagination.pages,
        'total_items': pagination.total,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next,
        'prev_num': pagination.prev_num,
        'next_num': pagination.next_num
    } 