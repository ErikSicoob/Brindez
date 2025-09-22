"""
Modelos de dados para acesso ao banco SQLite
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .schema import db_schema

class BaseModel:
    """Classe base para todos os modelos"""
    
    def __init__(self):
        self.db = db_schema
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com o banco"""
        return self.db.get_connection()
    
    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """Executa query SELECT"""
        return self.db.execute_query(query, params)
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Executa query UPDATE/INSERT/DELETE"""
        return self.db.execute_update(query, params)

class FilialModel(BaseModel):
    """Modelo para gerenciar filiais"""
    
    def get_all(self, ativo_apenas: bool = True) -> List[Dict[str, Any]]:
        """Retorna todas as filiais"""
        query = "SELECT * FROM filiais"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY numero"
        
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def get_by_id(self, filial_id: int) -> Optional[Dict[str, Any]]:
        """Retorna filial por ID"""
        query = "SELECT * FROM filiais WHERE id = ?"
        rows = self.execute_query(query, (filial_id,))
        return dict(rows[0]) if rows else None
    
    def get_by_numero(self, numero: str) -> Optional[Dict[str, Any]]:
        """Retorna filial por número"""
        query = "SELECT * FROM filiais WHERE numero = ?"
        rows = self.execute_query(query, (numero,))
        return dict(rows[0]) if rows else None
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria nova filial"""
        query = """
            INSERT INTO filiais (numero, nome, cidade, endereco, telefone, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (
                data['numero'], data['nome'], data['cidade'],
                data.get('endereco'), data.get('telefone'), data.get('email')
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update(self, filial_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza filial"""
        query = """
            UPDATE filiais 
            SET numero = ?, nome = ?, cidade = ?, endereco = ?, telefone = ?, email = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        affected = self.execute_update(query, (
            data['numero'], data['nome'], data['cidade'],
            data.get('endereco'), data.get('telefone'), data.get('email'),
            filial_id
        ))
        return affected > 0
    
    def toggle_ativo(self, filial_id: int) -> bool:
        """Ativa/desativa filial"""
        query = """
            UPDATE filiais 
            SET ativo = NOT ativo, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        affected = self.execute_update(query, (filial_id,))
        return affected > 0

class CategoriaModel(BaseModel):
    """Modelo para gerenciar categorias"""
    
    def get_all(self, ativo_apenas: bool = True) -> List[Dict[str, Any]]:
        """Retorna todas as categorias"""
        query = "SELECT * FROM categorias"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def get_by_id(self, categoria_id: int) -> Optional[Dict[str, Any]]:
        """Retorna categoria por ID"""
        query = "SELECT * FROM categorias WHERE id = ?"
        rows = self.execute_query(query, (categoria_id,))
        return dict(rows[0]) if rows else None
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria nova categoria"""
        query = "INSERT INTO categorias (nome, descricao) VALUES (?, ?)"
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (data['nome'], data.get('descricao')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update(self, categoria_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza categoria"""
        query = """
            UPDATE categorias 
            SET nome = ?, descricao = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        affected = self.execute_update(query, (
            data['nome'], data.get('descricao'), categoria_id
        ))
        return affected > 0
    
    def can_delete(self, categoria_id: int) -> Tuple[bool, str]:
        """Verifica se categoria pode ser excluída"""
        query = "SELECT COUNT(*) FROM brindes WHERE categoria_id = ? AND ativo = 1"
        rows = self.execute_query(query, (categoria_id,))
        count = rows[0][0] if rows else 0
        
        if count > 0:
            return False, f"Categoria possui {count} itens cadastrados"
        return True, ""

class UnidadeMedidaModel(BaseModel):
    """Modelo para gerenciar unidades de medida"""
    
    def get_all(self, ativo_apenas: bool = True) -> List[Dict[str, Any]]:
        """Retorna todas as unidades de medida"""
        query = "SELECT * FROM unidades_medida"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY codigo"
        
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def get_by_id(self, unidade_id: int) -> Optional[Dict[str, Any]]:
        """Retorna unidade por ID"""
        query = "SELECT * FROM unidades_medida WHERE id = ?"
        rows = self.execute_query(query, (unidade_id,))
        return dict(rows[0]) if rows else None
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria nova unidade de medida"""
        query = "INSERT INTO unidades_medida (codigo, descricao) VALUES (?, ?)"
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (data['codigo'], data['descricao']))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

class UsuarioModel(BaseModel):
    """Modelo para gerenciar usuários"""
    
    def get_all(self, ativo_apenas: bool = True) -> List[Dict[str, Any]]:
        """Retorna todos os usuários com dados da filial"""
        query = """
            SELECT u.*, f.nome as filial_nome 
            FROM usuarios u
            JOIN filiais f ON u.filial_id = f.id
        """
        if ativo_apenas:
            query += " WHERE u.ativo = 1"
        query += " ORDER BY u.nome"
        
        rows = self.execute_query(query)
        return [dict(row) for row in rows]
    
    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retorna usuário por username com dados da filial"""
        query = """
            SELECT u.*, f.nome as filial_nome, f.numero as filial_numero
            FROM usuarios u
            JOIN filiais f ON u.filial_id = f.id
            WHERE u.username = ? AND u.ativo = 1
        """
        rows = self.execute_query(query, (username,))
        return dict(rows[0]) if rows else None
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria novo usuário"""
        query = """
            INSERT INTO usuarios (username, nome, email, filial_id, perfil)
            VALUES (?, ?, ?, ?, ?)
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (
                data['username'], data['nome'], data.get('email'),
                data['filial_id'], data['perfil']
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

class BrindeModel(BaseModel):
    """Modelo para gerenciar brindes"""
    
    def get_all(self, filial_id: int = None, ativo_apenas: bool = True) -> List[Dict[str, Any]]:
        """Retorna todos os brindes com dados relacionados"""
        query = """
            SELECT b.*, c.nome as categoria_nome, u.codigo as unidade_codigo,
                   f.nome as filial_nome, f.numero as filial_numero
            FROM brindes b
            JOIN categorias c ON b.categoria_id = c.id
            JOIN unidades_medida u ON b.unidade_medida_id = u.id
            JOIN filiais f ON b.filial_id = f.id
        """
        
        conditions = []
        params = []
        
        if ativo_apenas:
            conditions.append("b.ativo = 1")
        
        if filial_id:
            conditions.append("b.filial_id = ?")
            params.append(filial_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY b.codigo"
        
        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]
    
    def get_by_id(self, brinde_id: int) -> Optional[Dict[str, Any]]:
        """Retorna brinde por ID com dados relacionados"""
        query = """
            SELECT b.*, c.nome as categoria_nome, u.codigo as unidade_codigo,
                   f.nome as filial_nome, f.numero as filial_numero
            FROM brindes b
            JOIN categorias c ON b.categoria_id = c.id
            JOIN unidades_medida u ON b.unidade_medida_id = u.id
            JOIN filiais f ON b.filial_id = f.id
            WHERE b.id = ?
        """
        rows = self.execute_query(query, (brinde_id,))
        return dict(rows[0]) if rows else None
    
    def get_by_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Retorna brinde por código"""
        query = """
            SELECT b.*, c.nome as categoria_nome, u.codigo as unidade_codigo,
                   f.nome as filial_nome
            FROM brindes b
            JOIN categorias c ON b.categoria_id = c.id
            JOIN unidades_medida u ON b.unidade_medida_id = u.id
            JOIN filiais f ON b.filial_id = f.id
            WHERE b.codigo = ?
        """
        rows = self.execute_query(query, (codigo,))
        return dict(rows[0]) if rows else None
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria novo brinde"""
        # Gerar próximo código
        codigo = self.get_next_codigo()
        
        query = """
            INSERT INTO brindes (codigo, descricao, categoria_id, quantidade, 
                               valor_unitario, unidade_medida_id, filial_id, 
                               observacoes, usuario_criacao_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (
                codigo, data['descricao'], data['categoria_id'], data['quantidade'],
                data['valor_unitario'], data['unidade_medida_id'], data['filial_id'],
                data.get('observacoes'), data.get('usuario_criacao_id')
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def update(self, brinde_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza brinde"""
        query = """
            UPDATE brindes 
            SET descricao = ?, categoria_id = ?, quantidade = ?, valor_unitario = ?,
                unidade_medida_id = ?, filial_id = ?, observacoes = ?,
                data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        affected = self.execute_update(query, (
            data['descricao'], data['categoria_id'], data['quantidade'],
            data['valor_unitario'], data['unidade_medida_id'], data['filial_id'],
            data.get('observacoes'), brinde_id
        ))
        return affected > 0
    
    def update_quantidade(self, brinde_id: int, nova_quantidade: int) -> bool:
        """Atualiza apenas a quantidade do brinde"""
        query = """
            UPDATE brindes 
            SET quantidade = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        affected = self.execute_update(query, (nova_quantidade, brinde_id))
        return affected > 0
    
    def get_next_codigo(self) -> str:
        """Gera próximo código sequencial"""
        query = "SELECT MAX(CAST(codigo AS INTEGER)) FROM brindes WHERE codigo GLOB '[0-9]*'"
        rows = self.execute_query(query)
        max_codigo = rows[0][0] if rows and rows[0][0] else 0
        return f"{max_codigo + 1:03d}"
    
    def search(self, termo: str, categoria_id: int = None, filial_id: int = None) -> List[Dict[str, Any]]:
        """Busca brindes por termo"""
        query = """
            SELECT b.*, c.nome as categoria_nome, u.codigo as unidade_codigo,
                   f.nome as filial_nome
            FROM brindes b
            JOIN categorias c ON b.categoria_id = c.id
            JOIN unidades_medida u ON b.unidade_medida_id = u.id
            JOIN filiais f ON b.filial_id = f.id
            WHERE b.ativo = 1 AND (b.descricao LIKE ? OR b.codigo LIKE ?)
        """
        
        params = [f"%{termo}%", f"%{termo}%"]
        
        if categoria_id:
            query += " AND b.categoria_id = ?"
            params.append(categoria_id)
        
        if filial_id:
            query += " AND b.filial_id = ?"
            params.append(filial_id)
        
        query += " ORDER BY b.codigo"
        
        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

class MovimentacaoModel(BaseModel):
    """Modelo para gerenciar movimentações"""
    
    def create(self, data: Dict[str, Any]) -> int:
        """Cria nova movimentação"""
        query = """
            INSERT INTO movimentacoes (brinde_id, tipo, quantidade, valor_unitario_anterior,
                                     valor_unitario_novo, justificativa, observacoes, destino,
                                     filial_origem_id, filial_destino_id, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, (
                data['brinde_id'], data['tipo'], data['quantidade'],
                data.get('valor_unitario_anterior'), data.get('valor_unitario_novo'),
                data.get('justificativa'), data.get('observacoes'), data.get('destino'),
                data.get('filial_origem_id'), data.get('filial_destino_id'),
                data['usuario_id']
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_by_brinde(self, brinde_id: int, limit: int = None) -> List[Dict[str, Any]]:
        """Retorna movimentações de um brinde"""
        query = """
            SELECT m.*, b.descricao as brinde_descricao, u.nome as usuario_nome,
                   fo.nome as filial_origem_nome, fd.nome as filial_destino_nome
            FROM movimentacoes m
            JOIN brindes b ON m.brinde_id = b.id
            JOIN usuarios u ON m.usuario_id = u.id
            LEFT JOIN filiais fo ON m.filial_origem_id = fo.id
            LEFT JOIN filiais fd ON m.filial_destino_id = fd.id
            WHERE m.brinde_id = ?
            ORDER BY m.data_hora DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = self.execute_query(query, (brinde_id,))
        return [dict(row) for row in rows]
    
    def get_recent(self, limit: int = 50, tipo: str = None) -> List[Dict[str, Any]]:
        """Retorna movimentações recentes"""
        query = """
            SELECT m.*, b.descricao as brinde_descricao, b.codigo as brinde_codigo,
                   u.nome as usuario_nome, fo.nome as filial_origem_nome, 
                   fd.nome as filial_destino_nome
            FROM movimentacoes m
            JOIN brindes b ON m.brinde_id = b.id
            JOIN usuarios u ON m.usuario_id = u.id
            LEFT JOIN filiais fo ON m.filial_origem_id = fo.id
            LEFT JOIN filiais fd ON m.filial_destino_id = fd.id
        """
        
        params = []
        if tipo:
            query += " WHERE m.tipo = ?"
            params.append(tipo)
        
        query += " ORDER BY m.data_hora DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]

# Instâncias dos modelos
filial_model = FilialModel()
categoria_model = CategoriaModel()
unidade_medida_model = UnidadeMedidaModel()
usuario_model = UsuarioModel()
brinde_model = BrindeModel()
movimentacao_model = MovimentacaoModel()
