"""
Sistema de validações e regras de negócio
"""

import re
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime

class ValidationError(Exception):
    """Exceção para erros de validação"""
    pass

class BusinessRuleError(Exception):
    """Exceção para violações de regras de negócio"""
    pass

class Validators:
    """Classe com validadores comuns"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> None:
        """Valida campo obrigatório"""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"O campo '{field_name}' é obrigatório")
    
    @staticmethod
    def validate_positive_number(value: Any, field_name: str) -> float:
        """Valida número positivo"""
        try:
            if isinstance(value, str):
                # Substituir vírgula por ponto para números decimais
                value = value.replace(',', '.')
            
            num = float(value)
            if num <= 0:
                raise ValidationError(f"O campo '{field_name}' deve ser um número positivo")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"O campo '{field_name}' deve ser um número válido")
    
    @staticmethod
    def validate_non_negative_number(value: Any, field_name: str) -> float:
        """Valida número não negativo"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
            
            num = float(value)
            if num < 0:
                raise ValidationError(f"O campo '{field_name}' não pode ser negativo")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"O campo '{field_name}' deve ser um número válido")
    
    @staticmethod
    def validate_integer(value: Any, field_name: str) -> int:
        """Valida número inteiro"""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"O campo '{field_name}' deve ser um número inteiro")
    
    @staticmethod
    def validate_positive_integer(value: Any, field_name: str) -> int:
        """Valida número inteiro positivo"""
        try:
            num = int(value)
            if num <= 0:
                raise ValidationError(f"O campo '{field_name}' deve ser um número inteiro positivo")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"O campo '{field_name}' deve ser um número inteiro válido")
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 0, max_length: int = None) -> str:
        """Valida comprimento de string"""
        if not isinstance(value, str):
            raise ValidationError(f"O campo '{field_name}' deve ser um texto")
        
        length = len(value.strip())
        
        if length < min_length:
            raise ValidationError(f"O campo '{field_name}' deve ter pelo menos {min_length} caracteres")
        
        if max_length and length > max_length:
            raise ValidationError(f"O campo '{field_name}' deve ter no máximo {max_length} caracteres")
        
        return value.strip()
    
    @staticmethod
    def validate_email(value: str, field_name: str) -> str:
        """Valida formato de email"""
        if not isinstance(value, str):
            raise ValidationError(f"O campo '{field_name}' deve ser um texto")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip()):
            raise ValidationError(f"O campo '{field_name}' deve ter um formato de email válido")
        
        return value.strip().lower()
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[Any]) -> Any:
        """Valida se valor está entre as opções permitidas"""
        if value not in choices:
            choices_str = ", ".join(str(c) for c in choices)
            raise ValidationError(f"O campo '{field_name}' deve ser uma das opções: {choices_str}")
        
        return value

class BrindeValidator:
    """Validador específico para brindes"""
    
    @staticmethod
    def validate_brinde_data(data: Dict[str, Any], categorias: List[str], unidades: List[str], filiais: List[str]) -> Dict[str, Any]:
        """Valida dados de um brinde"""
        validated_data = {}
        
        # Descrição
        Validators.validate_required(data.get('descricao'), 'Descrição')
        validated_data['descricao'] = Validators.validate_string_length(
            data['descricao'], 'Descrição', min_length=3, max_length=200
        )
        
        # Categoria
        Validators.validate_required(data.get('categoria'), 'Categoria')
        validated_data['categoria'] = Validators.validate_choice(
            data['categoria'], 'Categoria', categorias
        )
        
        # Quantidade
        Validators.validate_required(data.get('quantidade'), 'Quantidade')
        validated_data['quantidade'] = Validators.validate_positive_integer(
            data['quantidade'], 'Quantidade'
        )
        
        # Valor unitário
        Validators.validate_required(data.get('valor_unitario'), 'Valor Unitário')
        validated_data['valor_unitario'] = Validators.validate_positive_number(
            data['valor_unitario'], 'Valor Unitário'
        )
        
        # Unidade de medida
        Validators.validate_required(data.get('unidade_medida'), 'Unidade de Medida')
        validated_data['unidade_medida'] = Validators.validate_choice(
            data['unidade_medida'], 'Unidade de Medida', unidades
        )
        
        # Filial
        Validators.validate_required(data.get('filial'), 'Filial')
        validated_data['filial'] = Validators.validate_choice(
            data['filial'], 'Filial', filiais
        )
        
        # Campos opcionais
        if data.get('codigo'):
            validated_data['codigo'] = Validators.validate_string_length(
                data['codigo'], 'Código', max_length=20
            )
        
        if data.get('observacoes'):
            validated_data['observacoes'] = Validators.validate_string_length(
                data['observacoes'], 'Observações', max_length=500
            )
        
        return validated_data

class MovimentacaoValidator:
    """Validador específico para movimentações"""
    
    @staticmethod
    def validate_entrada_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados de entrada de estoque"""
        validated_data = {}
        
        # Quantidade
        Validators.validate_required(data.get('quantidade'), 'Quantidade')
        validated_data['quantidade'] = Validators.validate_positive_integer(
            data['quantidade'], 'Quantidade'
        )
        
        # Valor unitário (opcional)
        if data.get('valor_unitario'):
            validated_data['valor_unitario'] = Validators.validate_positive_number(
                data['valor_unitario'], 'Valor Unitário'
            )
        
        # Observações (opcional)
        if data.get('observacoes'):
            validated_data['observacoes'] = Validators.validate_string_length(
                data['observacoes'], 'Observações', max_length=500
            )
        
        return validated_data
    
    @staticmethod
    def validate_saida_data(data: Dict[str, Any], estoque_disponivel: int) -> Dict[str, Any]:
        """Valida dados de saída de estoque"""
        validated_data = {}
        
        # Quantidade
        Validators.validate_required(data.get('quantidade'), 'Quantidade')
        quantidade = Validators.validate_positive_integer(data['quantidade'], 'Quantidade')
        
        # Verificar se há estoque suficiente
        if quantidade > estoque_disponivel:
            raise BusinessRuleError(
                f"Quantidade solicitada ({quantidade}) é maior que o estoque disponível ({estoque_disponivel})"
            )
        
        validated_data['quantidade'] = quantidade
        
        # Justificativa (obrigatória)
        Validators.validate_required(data.get('justificativa'), 'Justificativa')
        validated_data['justificativa'] = Validators.validate_string_length(
            data['justificativa'], 'Justificativa', min_length=10, max_length=500
        )
        
        # Destino (opcional)
        if data.get('destino'):
            validated_data['destino'] = Validators.validate_string_length(
                data['destino'], 'Destino', max_length=200
            )
        
        return validated_data
    
    @staticmethod
    def validate_transferencia_data(data: Dict[str, Any], estoque_disponivel: int, filiais: List[str], filial_origem: str) -> Dict[str, Any]:
        """Valida dados de transferência"""
        validated_data = {}
        
        # Quantidade
        Validators.validate_required(data.get('quantidade'), 'Quantidade')
        quantidade = Validators.validate_positive_integer(data['quantidade'], 'Quantidade')
        
        # Verificar se há estoque suficiente
        if quantidade > estoque_disponivel:
            raise BusinessRuleError(
                f"Quantidade solicitada ({quantidade}) é maior que o estoque disponível ({estoque_disponivel})"
            )
        
        validated_data['quantidade'] = quantidade
        
        # Filial destino
        Validators.validate_required(data.get('filial_destino'), 'Filial de Destino')
        filial_destino = Validators.validate_choice(
            data['filial_destino'], 'Filial de Destino', filiais
        )
        
        # Verificar se não é a mesma filial
        if filial_destino == filial_origem:
            raise BusinessRuleError("A filial de destino deve ser diferente da filial de origem")
        
        validated_data['filial_destino'] = filial_destino
        
        # Justificativa (obrigatória)
        Validators.validate_required(data.get('justificativa'), 'Justificativa')
        validated_data['justificativa'] = Validators.validate_string_length(
            data['justificativa'], 'Justificativa', min_length=10, max_length=500
        )
        
        return validated_data

class UsuarioValidator:
    """Validador específico para usuários"""
    
    @staticmethod
    def validate_usuario_data(data: Dict[str, Any], filiais: List[str], perfis: List[str] = None) -> Dict[str, Any]:
        """Valida dados de usuário"""
        if perfis is None:
            perfis = ['Admin', 'Gestor', 'Usuario']
        
        validated_data = {}
        
        # Username
        Validators.validate_required(data.get('username'), 'Nome de Usuário')
        validated_data['username'] = Validators.validate_string_length(
            data['username'], 'Nome de Usuário', min_length=3, max_length=50
        ).lower()
        
        # Nome
        Validators.validate_required(data.get('nome'), 'Nome')
        validated_data['nome'] = Validators.validate_string_length(
            data['nome'], 'Nome', min_length=3, max_length=100
        )
        
        # Filial
        Validators.validate_required(data.get('filial'), 'Filial')
        validated_data['filial'] = Validators.validate_choice(
            data['filial'], 'Filial', filiais
        )
        
        # Perfil
        Validators.validate_required(data.get('perfil'), 'Perfil')
        validated_data['perfil'] = Validators.validate_choice(
            data['perfil'], 'Perfil', perfis
        )
        
        # Email (opcional)
        if data.get('email'):
            validated_data['email'] = Validators.validate_email(data['email'], 'Email')
        
        return validated_data

class FilialValidator:
    """Validador específico para filiais"""
    
    @staticmethod
    def validate_filial_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados de filial"""
        validated_data = {}
        
        # Número
        Validators.validate_required(data.get('numero'), 'Número')
        validated_data['numero'] = Validators.validate_string_length(
            data['numero'], 'Número', min_length=1, max_length=10
        )
        
        # Nome
        Validators.validate_required(data.get('nome'), 'Nome')
        validated_data['nome'] = Validators.validate_string_length(
            data['nome'], 'Nome', min_length=3, max_length=100
        )
        
        # Cidade
        Validators.validate_required(data.get('cidade'), 'Cidade')
        validated_data['cidade'] = Validators.validate_string_length(
            data['cidade'], 'Cidade', min_length=2, max_length=100
        )
        
        return validated_data

class BusinessRules:
    """Regras de negócio do sistema"""
    
    @staticmethod
    def can_delete_brinde(brinde_id: int, movimentacoes: List[Dict]) -> Tuple[bool, str]:
        """Verifica se um brinde pode ser excluído"""
        # Verificar se há movimentações associadas
        has_movements = any(mov.get('brinde_id') == brinde_id for mov in movimentacoes)
        
        if has_movements:
            return False, "Não é possível excluir um brinde que possui movimentações registradas"
        
        return True, ""
    
    @staticmethod
    def can_delete_categoria(categoria: str, brindes: List[Dict]) -> Tuple[bool, str]:
        """Verifica se uma categoria pode ser excluída"""
        # Verificar se há brindes usando esta categoria
        has_items = any(brinde.get('categoria') == categoria for brinde in brindes)
        
        if has_items:
            return False, "Não é possível excluir uma categoria que possui itens cadastrados"
        
        return True, ""
    
    @staticmethod
    def can_delete_unidade_medida(unidade: str, brindes: List[Dict]) -> Tuple[bool, str]:
        """Verifica se uma unidade de medida pode ser excluída"""
        # Verificar se há brindes usando esta unidade
        has_items = any(brinde.get('unidade_medida') == unidade for brinde in brindes)
        
        if has_items:
            return False, "Não é possível excluir uma unidade de medida que está sendo utilizada"
        
        return True, ""
    
    @staticmethod
    def can_delete_filial(filial: str, brindes: List[Dict], usuarios: List[Dict]) -> Tuple[bool, str]:
        """Verifica se uma filial pode ser excluída"""
        # Verificar se há brindes nesta filial
        has_items = any(brinde.get('filial') == filial for brinde in brindes)
        if has_items:
            return False, "Não é possível excluir uma filial que possui itens em estoque"
        
        # Verificar se há usuários nesta filial
        has_users = any(usuario.get('filial') == filial for usuario in usuarios)
        if has_users:
            return False, "Não é possível excluir uma filial que possui usuários cadastrados"
        
        return True, ""
    
    @staticmethod
    def validate_estoque_minimo(quantidade: int, estoque_minimo: int) -> bool:
        """Verifica se o estoque está abaixo do mínimo"""
        return quantidade <= estoque_minimo
    
    @staticmethod
    def calculate_valor_total_estoque(brindes: List[Dict]) -> float:
        """Calcula o valor total do estoque"""
        return sum(
            brinde.get('quantidade', 0) * brinde.get('valor_unitario', 0) 
            for brinde in brindes
        )
    
    @staticmethod
    def get_itens_estoque_baixo(brindes: List[Dict], estoque_minimo: int) -> List[Dict]:
        """Retorna itens com estoque baixo"""
        return [
            brinde for brinde in brindes 
            if brinde.get('quantidade', 0) <= estoque_minimo
        ]
