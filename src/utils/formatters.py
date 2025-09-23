def format_currency(value):
    """Formata um valor numérico como moeda brasileira (R$)."""
    if value is None:
        return "R$ 0,00"
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_relative_time(dt):
    """Formata uma data/hora para um formato relativo (ex: 'há 2 dias')."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    if diff.days > 0:
        return f"há {diff.days} dias"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"há {hours} hora{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"há {minutes} minuto{'s' if minutes > 1 else ''}"
    else:
        return "agora"