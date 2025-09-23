"""
Gerenciador de dados que integra SQLite com o sistema existente
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .models import (
    filial_model, categoria_model, unidade_medida_model, 
    usuario_model, brinde_model, movimentacao_model
)
from .schema import db_schema
from ..utils.audit_logger import audit_logger

class DatabaseDataManager:
    """Gerenciador de dados usando SQLite"""
    
    def __init__(self):
        """Inicializa o gerenciador"""
        self.db = db_schema
        
        # Cache para melhorar performance
        self._cache = {
            'categorias': None,
            'unidades_medida': None,
            'filiais': None,
            'configuracoes': None
        }
    
    def clear_cache(self):
        """Limpa o cache"""
        for key in self._cache:
            self._cache[key] = None
    
    # Métodos de configuração
    def get_configuracao(self, chave: str, valor_padrao: Any = None) -> Any:
        """Obtém valor de configuração"""
        if not self._cache['configuracoes']:
            query = "SELECT chave, valor FROM configuracoes"
            rows = self.db.execute_query(query)
            self._cache['configuracoes'] = {row[0]: row[1] for row in rows}
        
        valor = self._cache['configuracoes'].get(chave, valor_padrao)
        
        # Converter tipos básicos
        if valor == 'true':
            return True
        elif valor == 'false':
            return False
        elif valor and valor.isdigit():
            return int(valor)
        
        return valor
    
    def set_configuracao(self, chave: str, valor: Any) -> bool:
        """Define valor de configuração"""
        query = """
            INSERT OR REPLACE INTO configuracoes (chave, valor, data_atualizacao)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """
        affected = self.db.execute_update(query, (chave, str(valor)))
        if affected > 0:
            self._cache['configuracoes'] = None  # Limpar cache
        return affected > 0
    
    # Métodos para Filiais
    def get_filiais(self) -> List[Dict[str, Any]]:
        """Retorna lista de dicionários de filiais ativas"""
        if not self._cache['filiais']:
            self._cache['filiais'] = filial_model.get_all(ativo_apenas=True)
        return self._cache['filiais']

    def get_filiais_completas(self) -> List[Dict[str, Any]]:
        """Retorna dados completos das filiais"""
        return filial_model.get_all(ativo_apenas=True)
    
    def get_filial_by_nome(self, nome: str) -> Optional[Dict[str, Any]]:
        """Retorna filial por nome"""
        filiais = filial_model.get_all(ativo_apenas=False)
        return next((f for f in filiais if f['nome'] == nome), None)
    
    # Métodos para Categorias
    def get_categorias(self) -> List[str]:
        """Retorna lista de nomes de categorias ativas"""
        if not self._cache['categorias']:
            categorias = categoria_model.get_all(ativo_apenas=True)
            self._cache['categorias'] = [c['nome'] for c in categorias]
        return self._cache['categorias']
    
    def get_categorias_completas(self) -> List[Dict[str, Any]]:
        """Retorna dados completos das categorias"""
        return categoria_model.get_all(ativo_apenas=True)
    
    def get_categoria_by_nome(self, nome: str) -> Optional[Dict[str, Any]]:
        """Retorna categoria por nome"""
        categorias = categoria_model.get_all(ativo_apenas=False)
        return next((c for c in categorias if c['nome'] == nome), None)
    
    # Métodos para Unidades de Medida
    def get_unidades_medida(self) -> List[str]:
        """Retorna lista de códigos de unidades ativas"""
        if not self._cache['unidades_medida']:
            unidades = unidade_medida_model.get_all(ativo_apenas=True)
            self._cache['unidades_medida'] = [u['codigo'] for u in unidades]
        return self._cache['unidades_medida']
    
    def get_unidades_completas(self) -> List[Dict[str, Any]]:
        """Retorna dados completos das unidades"""
        return unidade_medida_model.get_all(ativo_apenas=True)
    
    def get_unidades_medida_completas(self) -> List[Dict[str, Any]]:
        """Retorna dados completos das unidades de medida (alias)"""
        return self.get_unidades_completas()
    
    # Métodos para Usuários
    def get_usuario_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retorna usuário por username"""
        return usuario_model.get_by_username(username)
    
    def get_usuarios_completos(self) -> List[Dict[str, Any]]:
        """Retorna dados completos dos usuários"""
        return usuario_model.get_all(ativo_apenas=True)
    
    # Métodos para Brindes
    def get_brindes(self, filial_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna lista de brindes"""
        filial_id = None
        if filial_filter and filial_filter != "Todas":
            filial = self.get_filial_by_nome(filial_filter)
            if filial:
                filial_id = filial['id']
        
        brindes_db = brinde_model.get_all(filial_id=filial_id, ativo_apenas=True)
        
        # Converter para formato compatível com mock_data
        brindes = []
        for brinde in brindes_db:
            brindes.append({
                'id': brinde['id'],
                'codigo': brinde['codigo'],
                'descricao': brinde['descricao'],
                'categoria': brinde['categoria_nome'],
                'quantidade': brinde['quantidade'],
                'valor_unitario': float(brinde['valor_unitario']),
                'unidade_medida': brinde['unidade_codigo'],
                'filial': brinde['filial_nome'],
                'observacoes': brinde.get('observacoes', ''),
                'data_cadastro': brinde['data_criacao'],
                'data_atualizacao': brinde.get('data_atualizacao')
            })
        
        return brindes
    
    def get_brinde_by_id(self, brinde_id: int) -> Optional[Dict[str, Any]]:
        """Retorna brinde por ID"""
        brinde_db = brinde_model.get_by_id(brinde_id)
        if not brinde_db:
            return None
        
        return {
            'id': brinde_db['id'],
            'codigo': brinde_db['codigo'],
            'descricao': brinde_db['descricao'],
            'categoria': brinde_db['categoria_nome'],
            'quantidade': brinde_db['quantidade'],
            'valor_unitario': float(brinde_db['valor_unitario']),
            'unidade_medida': brinde_db['unidade_codigo'],
            'filial': brinde_db['filial_nome'],
            'observacoes': brinde_db.get('observacoes', ''),
            'data_cadastro': brinde_db['data_criacao']
        }
    
    def create_brinde(self, brinde_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo brinde"""
        # Converter nomes para IDs
        categoria = self.get_categoria_by_nome(brinde_data['categoria'])
        if not categoria:
            raise ValueError(f"Categoria '{brinde_data['categoria']}' não encontrada")
        
        unidade = next((u for u in self.get_unidades_completas() 
                       if u['codigo'] == brinde_data['unidade_medida']), None)
        if not unidade:
            raise ValueError(f"Unidade de medida '{brinde_data['unidade_medida']}' não encontrada")
        
        filial = self.get_filial_by_nome(brinde_data['filial'])
        if not filial:
            raise ValueError(f"Filial '{brinde_data['filial']}' não encontrada")
        
        # Preparar dados para inserção
        data_insert = {
            'descricao': brinde_data['descricao'],
            'categoria_id': categoria['id'],
            'quantidade': int(brinde_data['quantidade']),
            'valor_unitario': float(str(brinde_data['valor_unitario']).replace(',', '.')),
            'unidade_medida_id': unidade['id'],
            'filial_id': filial['id'],
            'observacoes': brinde_data.get('observacoes', ''),
            'usuario_criacao_id': self._get_usuario_id(brinde_data.get('usuario_cadastro'))
        }
        
        # Inserir no banco
        brinde_id = brinde_model.create(data_insert)
        
        # Limpar cache
        self.clear_cache()
        
        # Retornar brinde criado
        brinde_criado = self.get_brinde_by_id(brinde_id)
        
        # Auditoria
        audit_logger.audit_brinde_created(brinde_criado, data_insert.get('usuario_criacao_id'))
        
        return brinde_criado
    
    def update_brinde(self, brinde_id: int, brinde_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um brinde"""
        # Converter nomes para IDs
        categoria = self.get_categoria_by_nome(brinde_data['categoria'])
        unidade = next((u for u in self.get_unidades_completas() 
                       if u['codigo'] == brinde_data['unidade_medida']), None)
        filial = self.get_filial_by_nome(brinde_data['filial'])
        
        if not all([categoria, unidade, filial]):
            return None
        
        # Preparar dados para atualização
        data_update = {
            'descricao': brinde_data['descricao'],
            'categoria_id': categoria['id'],
            'quantidade': int(brinde_data['quantidade']),
            'valor_unitario': float(str(brinde_data['valor_unitario']).replace(',', '.')),
            'unidade_medida_id': unidade['id'],
            'filial_id': filial['id'],
            'observacoes': brinde_data.get('observacoes', '')
        }
        
        # Obter dados anteriores para auditoria
        brinde_anterior = self.get_brinde_by_id(brinde_id)
        
        # Atualizar no banco
        success = brinde_model.update(brinde_id, data_update)
        
        if success:
            self.clear_cache()
            brinde_atualizado = self.get_brinde_by_id(brinde_id)
            
            # Auditoria
            audit_logger.audit_brinde_updated(brinde_id, brinde_anterior, brinde_atualizado)
            
            return brinde_atualizado
        
        return None
    
    def update_estoque_brinde(self, brinde_id: int, quantidade: int, tipo: str) -> bool:
        """Atualiza estoque de um brinde"""
        brinde = brinde_model.get_by_id(brinde_id)
        if not brinde:
            return False
        
        estoque_atual = brinde['quantidade']
        
        if tipo == 'entrada':
            novo_estoque = estoque_atual + quantidade
        elif tipo == 'saida':
            novo_estoque = estoque_atual - quantidade
            if novo_estoque < 0:
                raise ValueError("Estoque insuficiente")
        else:
            return False
        
        return brinde_model.update_quantidade(brinde_id, novo_estoque)
    
    def find_or_create_brinde_for_transfer(self, brinde_origem: Dict[str, Any], filial_destino_nome: str, username: str) -> Dict[str, Any]:
        """
        Encontra um brinde com a mesma descrição na filial de destino.
        Se não encontrar, cria um novo com estoque zero.
        """
        # Verificar se já existe um brinde com a mesma descrição na filial de destino
        brindes_destino = self.get_brindes(filial_filter=filial_destino_nome)
        brinde_destino_existente = next((b for b in brindes_destino if b['descricao'] == brinde_origem['descricao']), None)

        if brinde_destino_existente:
            return brinde_destino_existente

        # Se não existir, criar um novo brinde na filial de destino com estoque zero
        else:
            novo_brinde_data = {
                'descricao': brinde_origem['descricao'],
                'categoria': brinde_origem['categoria'],
                'quantidade': 0, # Começa com zero, a movimentação irá adicionar o estoque
                'valor_unitario': brinde_origem['valor_unitario'],
                'unidade_medida': brinde_origem['unidade_medida'],
                'filial': filial_destino_nome,
                'usuario_cadastro': username
            }
            return self.create_brinde(novo_brinde_data)

    def search_brindes(self, query: str, categoria: str = None, filial: str = None) -> List[Dict[str, Any]]:
        """Busca brindes por critérios"""
        categoria_id = None
        if categoria and categoria != "Todas":
            cat = self.get_categoria_by_nome(categoria)
            if cat:
                categoria_id = cat['id']
        
        filial_id = None
        if filial and filial != "Todas":
            fil = self.get_filial_by_nome(filial)
            if fil:
                filial_id = fil['id']
        
        brindes_db = brinde_model.search(query, categoria_id, filial_id)
        
        # Converter para formato compatível
        brindes = []
        for brinde in brindes_db:
            brindes.append({
                'id': brinde['id'],
                'codigo': brinde['codigo'],
                'descricao': brinde['descricao'],
                'categoria': brinde['categoria_nome'],
                'quantidade': brinde['quantidade'],
                'valor_unitario': float(brinde['valor_unitario']),
                'unidade_medida': brinde['unidade_codigo'],
                'filial': brinde['filial_nome']
            })
        
        return brindes
    
    # Métodos para Movimentações
    def create_movimentacao(self, movimentacao_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova movimentação"""
        # Obter IDs necessários
        usuario_id = self._get_usuario_id(movimentacao_data.get('usuario'))
        
        filial_origem_id = None
        filial_destino_id = None
        
        if movimentacao_data.get('filial'):
            filial = self.get_filial_by_nome(movimentacao_data['filial'])
            if filial:
                filial_origem_id = filial['id']
        
        if movimentacao_data.get('filial_destino'):
            filial = self.get_filial_by_nome(movimentacao_data['filial_destino'])
            if filial:
                filial_destino_id = filial['id']
        
        if movimentacao_data.get('filial_origem'):
            filial = self.get_filial_by_nome(movimentacao_data['filial_origem'])
            if filial:
                filial_origem_id = filial['id']
        
        # Preparar dados para inserção
        data_insert = {
            'brinde_id': movimentacao_data['brinde_id'],
            'tipo': movimentacao_data['tipo'],
            'quantidade': int(movimentacao_data['quantidade']),
            'valor_unitario_anterior': movimentacao_data.get('valor_unitario_anterior'),
            'valor_unitario_novo': movimentacao_data.get('valor_unitario_novo'),
            'justificativa': movimentacao_data.get('justificativa'),
            'observacoes': movimentacao_data.get('observacoes'),
            'destino': movimentacao_data.get('destino'),
            'filial_origem_id': filial_origem_id,
            'filial_destino_id': filial_destino_id,
            'usuario_id': usuario_id or 1  # Fallback para admin
        }
        
        # Atualizar estoque do brinde
        brinde_id = movimentacao_data['brinde_id']
        quantidade = movimentacao_data['quantidade']
        tipo = movimentacao_data['tipo']
        
        if 'entrada' in tipo:
            self.update_estoque_brinde(brinde_id, quantidade, 'entrada')
        elif 'saida' in tipo:
            self.update_estoque_brinde(brinde_id, quantidade, 'saida')
        
        # Inserir movimentação
        movimentacao_id = movimentacao_model.create(data_insert)
        
        # Retornar dados da movimentação
        movimentacao_criada = {
            'id': movimentacao_id,
            'data_hora': datetime.now().isoformat(),
            **movimentacao_data
        }
        
        # Auditoria
        audit_logger.audit_movimentacao_created(movimentacao_criada, data_insert.get('usuario_id'))
        
        return movimentacao_criada
    
    def get_movimentacoes(self, brinde_id: int = None, tipo: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém lista de movimentações"""
        if brinde_id:
            movs = movimentacao_model.get_by_brinde(brinde_id, limit)
        else:
            movs = movimentacao_model.get_recent(limit, tipo)
        
        # Converter para formato compatível
        movimentacoes = []
        for mov in movs:
            movimentacoes.append({
                'id': mov['id'],
                'brinde_id': mov['brinde_id'],
                'brinde_codigo': mov.get('brinde_codigo', ''),
                'brinde_descricao': mov['brinde_descricao'],
                'tipo': mov['tipo'],
                'quantidade': mov['quantidade'],
                'usuario': mov['usuario_nome'],
                'justificativa': mov.get('justificativa', ''),
                'observacoes': mov.get('observacoes', ''),
                'destino': mov.get('destino', ''),
                'filial': mov.get('filial_origem_nome', ''),
                'filial_origem': mov.get('filial_origem_nome', ''),
                'filial_destino': mov.get('filial_destino_nome', ''),
                'data_hora': mov['data_hora']
            })
        
        return movimentacoes
    
    def _get_usuario_id(self, username: str) -> Optional[int]:
        """Obtém ID do usuário por username"""
        if not username:
            return None
        
        usuario = usuario_model.get_by_username(username)
        return usuario['id'] if usuario else None
    
    # Métodos CRUD - Categorias
    def create_categoria(self, categoria_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova categoria"""
        data_insert = {
            'nome': categoria_data['nome'],
            'descricao': categoria_data.get('descricao', ''),
            'ativa': categoria_data.get('ativa', True)
        }
        
        categoria_id = categoria_model.create(data_insert)
        self.clear_cache()
        
        categoria_criada = {
            'id': categoria_id,
            **categoria_data
        }
        
        # Auditoria
        audit_logger.audit_categoria_created(categoria_criada, data_insert.get('usuario_id'))
        
        return categoria_criada
    
    def update_categoria(self, categoria_id: int, categoria_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma categoria"""
        categoria_existente = categoria_model.get_by_id(categoria_id)
        if not categoria_existente:
            return None
        
        data_update = {
            'nome': categoria_data.get('nome', categoria_existente['nome']),
            'descricao': categoria_data.get('descricao', categoria_existente['descricao']),
            'ativa': categoria_data.get('ativa', categoria_existente['ativa'])
        }
        
        sucesso = categoria_model.update(categoria_id, data_update)
        if sucesso:
            self.clear_cache()
            categoria_atualizada = {
                'id': categoria_id,
                **data_update
            }
            
            # Auditoria
            audit_logger.audit_categoria_updated(categoria_atualizada, data_update.get('usuario_id'))
            
            return categoria_atualizada
        
        return None
    
    def delete_categoria(self, categoria_id: int) -> bool:
        """Exclui uma categoria"""
        sucesso = categoria_model.delete(categoria_id)
        if sucesso:
            self.clear_cache()
            
            # Auditoria
            audit_logger.audit_categoria_deleted(categoria_id, None)
        
        return sucesso
    
    # Métodos CRUD - Unidades de Medida
    def create_unidade_medida(self, unidade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova unidade de medida"""
        data_insert = {
            'codigo': unidade_data['codigo'].upper(),
            'descricao': unidade_data['descricao'],
            'ativa': unidade_data.get('ativa', True)
        }
        
        unidade_id = unidade_medida_model.create(data_insert)
        self.clear_cache()
        
        unidade_criada = {
            'id': unidade_id,
            **unidade_data
        }
        
        # Auditoria
        audit_logger.audit_unidade_created(unidade_criada, data_insert.get('usuario_id'))
        
        return unidade_criada
    
    def update_unidade_medida(self, unidade_id: int, unidade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma unidade de medida"""
        unidade_existente = unidade_medida_model.get_by_id(unidade_id)
        if not unidade_existente:
            return None
        
        data_update = {
            'codigo': unidade_data.get('codigo', unidade_existente['codigo']).upper(),
            'descricao': unidade_data.get('descricao', unidade_existente['descricao']),
            'ativa': unidade_data.get('ativa', unidade_existente['ativa'])
        }
        
        sucesso = unidade_medida_model.update(unidade_id, data_update)
        if sucesso:
            self.clear_cache()
            unidade_atualizada = {
                'id': unidade_id,
                **data_update
            }
            
            # Auditoria
            audit_logger.audit_unidade_updated(unidade_atualizada, data_update.get('usuario_id'))
            
            return unidade_atualizada
        
        return None
    
    def delete_unidade_medida(self, unidade_id: int) -> bool:
        """Exclui uma unidade de medida"""
        sucesso = unidade_medida_model.delete(unidade_id)
        if sucesso:
            self.clear_cache()
            
            # Auditoria
            audit_logger.audit_unidade_deleted(unidade_id, None)
        
        return sucesso
    
    # Métodos CRUD - Usuários
    def create_usuario(self, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo usuário"""
        # Buscar ID da filial
        filial = self.get_filial_by_nome(usuario_data['filial'])
        filial_id = filial['id'] if filial else None
        
        data_insert = {
            'username': usuario_data['username'],
            'nome': usuario_data['nome'],
            'email': usuario_data.get('email', ''),
            'filial_id': filial_id,
            'perfil': usuario_data['perfil'],
            'ativo': usuario_data.get('ativo', True)
        }
        
        usuario_id = usuario_model.create(data_insert)
        self.clear_cache()
        
        usuario_criado = {
            'id': usuario_id,
            **usuario_data
        }
        
        # Auditoria
        audit_logger.audit_usuario_created(usuario_criado, data_insert.get('usuario_id'))
        
        return usuario_criado
    
    def update_usuario(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um usuário"""
        usuario_existente = usuario_model.get_by_id(usuario_id)
        if not usuario_existente:
            return None
        
        # Buscar ID da filial se fornecida
        filial_id = usuario_existente['filial_id']
        if 'filial' in usuario_data:
            filial = self.get_filial_by_nome(usuario_data['filial'])
            filial_id = filial['id'] if filial else filial_id
        
        data_update = {
            'username': usuario_data.get('username', usuario_existente['username']),
            'nome': usuario_data.get('nome', usuario_existente['nome']),
            'email': usuario_data.get('email', usuario_existente['email']),
            'filial_id': filial_id,
            'perfil': usuario_data.get('perfil', usuario_existente['perfil']),
            'ativo': usuario_data.get('ativo', usuario_existente['ativo'])
        }
        
        sucesso = usuario_model.update(usuario_id, data_update)
        if sucesso:
            self.clear_cache()
            usuario_atualizado = {
                'id': usuario_id,
                **usuario_data
            }
            
            # Auditoria
            audit_logger.audit_usuario_updated(usuario_atualizado, data_update.get('usuario_id'))
            
            return usuario_atualizado
        
        return None
    
    def get_usuarios(self) -> List[Dict[str, Any]]:
        """Obtém lista de usuários"""
        usuarios_db = usuario_model.get_all()
        usuarios = []
        
        for usuario in usuarios_db:
            # Buscar nome da filial
            filial_nome = ''
            if usuario['filial_id']:
                filial = filial_model.get_by_id(usuario['filial_id'])
                filial_nome = filial['nome'] if filial else ''
            
            usuarios.append({
                'id': usuario['id'],
                'username': usuario['username'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'filial': filial_nome,
                'perfil': usuario['perfil'],
                'ativo': usuario['ativo']
            })
        
        return usuarios
    
    # Métodos CRUD - Filiais
    def create_filial(self, filial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova filial"""
        data_insert = {
            'numero': filial_data['numero'],
            'nome': filial_data['nome'],
            'endereco': filial_data.get('endereco', ''),
            'cidade': filial_data['cidade'],
            'telefone': filial_data.get('telefone', ''),
            'ativa': filial_data.get('ativa', True)
        }
        
        filial_id = filial_model.create(data_insert)
        self.clear_cache()
        
        filial_criada = {
            'id': filial_id,
            **filial_data
        }
        
        # Auditoria
        audit_logger.audit_filial_created(filial_criada, data_insert.get('usuario_id'))
        
        return filial_criada
    
    def update_filial(self, filial_id: int, filial_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza uma filial"""
        filial_existente = filial_model.get_by_id(filial_id)
        if not filial_existente:
            return None
        
        data_update = {
            'numero': filial_data.get('numero', filial_existente['numero']),
            'nome': filial_data.get('nome', filial_existente['nome']),
            'endereco': filial_data.get('endereco', filial_existente['endereco']),
            'cidade': filial_data.get('cidade', filial_existente['cidade']),
            'telefone': filial_data.get('telefone', filial_existente['telefone']),
            'ativa': filial_data.get('ativa', filial_existente['ativa'])
        }
        
        sucesso = filial_model.update(filial_id, data_update)
        if sucesso:
            self.clear_cache()
            filial_atualizada = {
                'id': filial_id,
                **data_update
            }
            
            # Auditoria
            audit_logger.audit_filial_updated(filial_atualizada, data_update.get('usuario_id'))
            
            return filial_atualizada
        
        return None
    
    def delete_brinde(self, brinde_id: int) -> bool:
        """Exclui um brinde"""
        sucesso = brinde_model.delete(brinde_id)
        if sucesso:
            self.clear_cache()
            
            # Auditoria
            audit_logger.audit_brinde_deleted(brinde_id, None)
        
        return sucesso
    
    # Métodos para estatísticas
    def get_estatisticas_dashboard(self) -> Dict[str, Any]:
        """Retorna estatísticas para o dashboard"""
        brindes = self.get_brindes()
        
        total_itens = sum(b['quantidade'] for b in brindes)
        total_categorias = len(self.get_categorias())
        valor_total = sum(b['quantidade'] * b['valor_unitario'] for b in brindes)
        estoque_minimo = self.get_configuracao('estoque_minimo', 10)
        itens_baixo = len([b for b in brindes if b['quantidade'] <= estoque_minimo])
        
        return {
            'total_itens': total_itens,
            'total_categorias': total_categorias,
            'valor_total': valor_total,
            'itens_estoque_baixo': itens_baixo,
            'estoque_minimo': estoque_minimo
        }

# Instância global do gerenciador
db_data_manager = DatabaseDataManager()
