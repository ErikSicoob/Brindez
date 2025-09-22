"""
Sistema de logs e auditoria
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from ..database.schema import db_schema

class AuditLogger:
    """Sistema de auditoria e logs"""
    
    def __init__(self):
        """Inicializa o sistema de auditoria"""
        self.setup_logging()
        self.db = db_schema
    
    def setup_logging(self):
        """Configura o sistema de logging"""
        # Criar diretório de logs se não existir
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Configurar logger principal
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/brindez.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('BrindeSystem')
        
        # Logger específico para auditoria
        self.audit_logger = logging.getLogger('Audit')
        audit_handler = logging.FileHandler('logs/audit.log', encoding='utf-8')
        audit_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
    
    def log_info(self, message: str, extra_data: Dict[str, Any] = None):
        """Log de informação"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, ensure_ascii=False)}"
        self.logger.info(message)
    
    def log_warning(self, message: str, extra_data: Dict[str, Any] = None):
        """Log de aviso"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, ensure_ascii=False)}"
        self.logger.warning(message)
    
    def log_error(self, message: str, exception: Exception = None, extra_data: Dict[str, Any] = None):
        """Log de erro"""
        if extra_data:
            message = f"{message} | Data: {json.dumps(extra_data, ensure_ascii=False)}"
        if exception:
            message = f"{message} | Exception: {str(exception)}"
        self.logger.error(message)
    
    def audit_action(self, 
                    tabela: str, 
                    acao: str, 
                    registro_id: Optional[int] = None,
                    dados_anteriores: Optional[Dict[str, Any]] = None,
                    dados_novos: Optional[Dict[str, Any]] = None,
                    usuario_id: Optional[int] = None,
                    ip_address: Optional[str] = None,
                    user_agent: Optional[str] = None):
        """Registra ação de auditoria"""
        
        # Log em arquivo
        audit_message = f"AUDIT: {acao} em {tabela}"
        if registro_id:
            audit_message += f" (ID: {registro_id})"
        if usuario_id:
            audit_message += f" por usuário {usuario_id}"
        
        self.audit_logger.info(audit_message)
        
        # Registrar no banco de dados
        try:
            query = """
                INSERT INTO logs_auditoria 
                (tabela, registro_id, acao, dados_anteriores, dados_novos, 
                 usuario_id, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            dados_anteriores_json = json.dumps(dados_anteriores, ensure_ascii=False) if dados_anteriores else None
            dados_novos_json = json.dumps(dados_novos, ensure_ascii=False) if dados_novos else None
            
            self.db.execute_update(query, (
                tabela, registro_id, acao, dados_anteriores_json, dados_novos_json,
                usuario_id, ip_address, user_agent
            ))
            
        except Exception as e:
            self.log_error(f"Erro ao registrar auditoria no banco", e)
    
    def audit_brinde_created(self, brinde_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de brinde"""
        self.audit_action(
            tabela='brindes',
            acao='INSERT',
            registro_id=brinde_data.get('id'),
            dados_novos=brinde_data,
            usuario_id=usuario_id
        )
        
        self.log_info(f"Brinde criado: {brinde_data.get('descricao')} (ID: {brinde_data.get('id')})")
    
    def audit_brinde_updated(self, brinde_id: int, dados_anteriores: Dict[str, Any], 
                           dados_novos: Dict[str, Any], usuario_id: int = None):
        """Auditoria de atualização de brinde"""
        self.audit_action(
            tabela='brindes',
            acao='UPDATE',
            registro_id=brinde_id,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            usuario_id=usuario_id
        )
        
        self.log_info(f"Brinde atualizado: ID {brinde_id}")
    
    def audit_brinde_deleted(self, brinde_id: int, brinde_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de exclusão de brinde"""
        self.audit_action(
            tabela='brindes',
            acao='DELETE',
            registro_id=brinde_id,
            dados_anteriores=brinde_data,
            usuario_id=usuario_id
        )
        
        self.log_info(f"Brinde excluído: {brinde_data.get('descricao')} (ID: {brinde_id})")
    
    def audit_movimentacao_created(self, movimentacao_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de movimentação"""
        self.audit_action(
            tabela='movimentacoes',
            acao='INSERT',
            registro_id=movimentacao_data.get('id'),
            dados_novos=movimentacao_data,
            usuario_id=usuario_id
        )
        
        tipo = movimentacao_data.get('tipo', '')
        quantidade = movimentacao_data.get('quantidade', 0)
        brinde_desc = movimentacao_data.get('brinde_descricao', '')
        
        self.log_info(f"Movimentação registrada: {tipo} de {quantidade} {brinde_desc}")
    
    def audit_user_login(self, username: str, success: bool, ip_address: str = None):
        """Auditoria de login de usuário"""
        status = "SUCCESS" if success else "FAILED"
        self.audit_action(
            tabela='usuarios',
            acao=f'LOGIN_{status}',
            dados_novos={'username': username, 'timestamp': datetime.now().isoformat()},
            ip_address=ip_address
        )
        
        self.log_info(f"Login {status.lower()}: {username}")
    
    def audit_config_changed(self, chave: str, valor_anterior: Any, valor_novo: Any, usuario_id: int = None):
        """Auditoria de mudança de configuração"""
        self.audit_action(
            tabela='configuracoes',
            acao='UPDATE',
            dados_anteriores={'chave': chave, 'valor': valor_anterior},
            dados_novos={'chave': chave, 'valor': valor_novo},
            usuario_id=usuario_id
        )
        
        self.log_info(f"Configuração alterada: {chave} = {valor_novo} (anterior: {valor_anterior})")
    
    def audit_backup_created(self, backup_path: str, usuario_id: int = None):
        """Auditoria de criação de backup"""
        self.audit_action(
            tabela='sistema',
            acao='BACKUP_CREATED',
            dados_novos={'backup_path': backup_path, 'timestamp': datetime.now().isoformat()},
            usuario_id=usuario_id
        )
        
        self.log_info(f"Backup criado: {backup_path}")
    
    def get_audit_logs(self, 
                      tabela: str = None, 
                      acao: str = None, 
                      usuario_id: int = None,
                      data_inicio: datetime = None,
                      data_fim: datetime = None,
                      limit: int = 100) -> list:
        """Obtém logs de auditoria"""
        
        query = """
            SELECT la.*, u.nome as usuario_nome
            FROM logs_auditoria la
            LEFT JOIN usuarios u ON la.usuario_id = u.id
            WHERE 1=1
        """
        
        params = []
        
        if tabela:
            query += " AND la.tabela = ?"
            params.append(tabela)
        
        if acao:
            query += " AND la.acao = ?"
            params.append(acao)
        
        if usuario_id:
            query += " AND la.usuario_id = ?"
            params.append(usuario_id)
        
        if data_inicio:
            query += " AND la.data_hora >= ?"
            params.append(data_inicio.isoformat())
        
        if data_fim:
            query += " AND la.data_hora <= ?"
            params.append(data_fim.isoformat())
        
        query += " ORDER BY la.data_hora DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            rows = self.db.execute_query(query, tuple(params) if params else None)
            return [dict(row) for row in rows]
        except Exception as e:
            self.log_error("Erro ao buscar logs de auditoria", e)
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do sistema"""
        try:
            stats = {}
            
            # Total de logs por tipo
            query = "SELECT acao, COUNT(*) as total FROM logs_auditoria GROUP BY acao"
            rows = self.db.execute_query(query)
            stats['logs_por_acao'] = {row[0]: row[1] for row in rows}
            
            # Logs por usuário
            query = """
                SELECT u.nome, COUNT(*) as total 
                FROM logs_auditoria la
                JOIN usuarios u ON la.usuario_id = u.id
                GROUP BY u.nome
                ORDER BY total DESC
                LIMIT 10
            """
            rows = self.db.execute_query(query)
            stats['logs_por_usuario'] = {row[0]: row[1] for row in rows}
            
            # Logs por data (últimos 7 dias)
            query = """
                SELECT DATE(data_hora) as data, COUNT(*) as total
                FROM logs_auditoria
                WHERE data_hora >= date('now', '-7 days')
                GROUP BY DATE(data_hora)
                ORDER BY data DESC
            """
            rows = self.db.execute_query(query)
            stats['logs_por_data'] = {row[0]: row[1] for row in rows}
            
            return stats
            
        except Exception as e:
            self.log_error("Erro ao obter estatísticas do sistema", e)
            return {}
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Remove logs antigos"""
        try:
            query = "DELETE FROM logs_auditoria WHERE data_hora < date('now', '-{} days')".format(days_to_keep)
            affected = self.db.execute_update(query)
            
            self.log_info(f"Limpeza de logs concluída: {affected} registros removidos")
            return affected
            
        except Exception as e:
            self.log_error("Erro na limpeza de logs", e)
            return 0
    
    # Métodos de auditoria para Categorias
    def audit_categoria_created(self, categoria_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de categoria"""
        self.audit_action(
            tabela='categorias',
            acao='INSERT',
            registro_id=categoria_data.get('id'),
            dados_novos=categoria_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Categoria criada: {categoria_data.get('nome')} (ID: {categoria_data.get('id')})")
    
    def audit_categoria_updated(self, categoria_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de atualização de categoria"""
        self.audit_action(
            tabela='categorias',
            acao='UPDATE',
            registro_id=categoria_data.get('id'),
            dados_novos=categoria_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Categoria atualizada: {categoria_data.get('nome')} (ID: {categoria_data.get('id')})")
    
    def audit_categoria_deleted(self, categoria_id: int, usuario_id: int = None):
        """Auditoria de exclusão de categoria"""
        self.audit_action(
            tabela='categorias',
            acao='DELETE',
            registro_id=categoria_id,
            usuario_id=usuario_id
        )
        self.log_info(f"Categoria excluída: ID {categoria_id}")
    
    # Métodos de auditoria para Unidades de Medida
    def audit_unidade_created(self, unidade_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de unidade"""
        self.audit_action(
            tabela='unidades_medida',
            acao='INSERT',
            registro_id=unidade_data.get('id'),
            dados_novos=unidade_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Unidade criada: {unidade_data.get('codigo')} (ID: {unidade_data.get('id')})")
    
    def audit_unidade_updated(self, unidade_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de atualização de unidade"""
        self.audit_action(
            tabela='unidades_medida',
            acao='UPDATE',
            registro_id=unidade_data.get('id'),
            dados_novos=unidade_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Unidade atualizada: {unidade_data.get('codigo')} (ID: {unidade_data.get('id')})")
    
    def audit_unidade_deleted(self, unidade_id: int, usuario_id: int = None):
        """Auditoria de exclusão de unidade"""
        self.audit_action(
            tabela='unidades_medida',
            acao='DELETE',
            registro_id=unidade_id,
            usuario_id=usuario_id
        )
        self.log_info(f"Unidade excluída: ID {unidade_id}")
    
    # Métodos de auditoria para Usuários
    def audit_usuario_created(self, usuario_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de usuário"""
        self.audit_action(
            tabela='usuarios',
            acao='INSERT',
            registro_id=usuario_data.get('id'),
            dados_novos=usuario_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Usuário criado: {usuario_data.get('username')} (ID: {usuario_data.get('id')})")
    
    def audit_usuario_updated(self, usuario_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de atualização de usuário"""
        self.audit_action(
            tabela='usuarios',
            acao='UPDATE',
            registro_id=usuario_data.get('id'),
            dados_novos=usuario_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Usuário atualizado: {usuario_data.get('username')} (ID: {usuario_data.get('id')})")
    
    # Métodos de auditoria para Filiais
    def audit_filial_created(self, filial_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de criação de filial"""
        self.audit_action(
            tabela='filiais',
            acao='INSERT',
            registro_id=filial_data.get('id'),
            dados_novos=filial_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Filial criada: {filial_data.get('nome')} (ID: {filial_data.get('id')})")
    
    def audit_filial_updated(self, filial_data: Dict[str, Any], usuario_id: int = None):
        """Auditoria de atualização de filial"""
        self.audit_action(
            tabela='filiais',
            acao='UPDATE',
            registro_id=filial_data.get('id'),
            dados_novos=filial_data,
            usuario_id=usuario_id
        )
        self.log_info(f"Filial atualizada: {filial_data.get('nome')} (ID: {filial_data.get('id')})")

# Instância global do logger de auditoria
audit_logger = AuditLogger()
