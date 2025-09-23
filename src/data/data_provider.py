"""
Provedor de dados que alterna entre mock e banco de dados
"""

import os
from typing import Dict, List, Any, Optional
from .mock_data import mock_data
from ..database.data_manager import db_data_manager
from ..utils.performance import performance_monitor, cache_manager

class DataProvider:
    """Provedor de dados que escolhe automaticamente entre mock e database"""
    
    def __init__(self):
        """Inicializa o provedor de dados"""
        self._use_database = self._should_use_database()
        self._current_provider = db_data_manager if self._use_database else mock_data
        
        print(f"DataProvider inicializado: {'Database' if self._use_database else 'Mock'}")
    
    def _should_use_database(self) -> bool:
        """Determina se deve usar o banco de dados"""
        # Verificar se existe arquivo de configuração para forçar mock
        if os.path.exists("use_mock.flag"):
            return False
        
        # Verificar se o banco SQLite está disponível
        try:
            from ..database.schema import db_schema
            # Tentar conectar e fazer uma query simples
            conn = db_schema.get_connection()
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao conectar com banco de dados, usando mock: {e}")
            return False
    
    def switch_to_database(self):
        """Força uso do banco de dados"""
        try:
            self._use_database = True
            self._current_provider = db_data_manager
            print("Alternado para Database")
        except Exception as e:
            print(f"Erro ao alternar para database: {e}")
            self._use_database = False
            self._current_provider = mock_data
    
    def switch_to_mock(self):
        """Força uso do mock"""
        self._use_database = False
        self._current_provider = mock_data
        print("Alternado para Mock")
    
    def is_using_database(self) -> bool:
        """Retorna se está usando banco de dados"""
        return self._use_database
    
    # Métodos delegados - Configurações
    def get_configuracao(self, chave: str, valor_padrao: Any = None) -> Any:
        """Obtém configuração"""
        if self._use_database:
            return self._current_provider.get_configuracao(chave, valor_padrao)
        else:
            return self._current_provider.data.get('configuracoes', {}).get(chave, valor_padrao)
    
    def set_configuracao(self, chave: str, valor: Any) -> bool:
        """Define configuração"""
        if self._use_database:
            return self._current_provider.set_configuracao(chave, valor)
        else:
            if 'configuracoes' not in self._current_provider.data:
                self._current_provider.data['configuracoes'] = {}
            self._current_provider.data['configuracoes'][chave] = valor
            self._current_provider.save_data()
            return True
    
    # Métodos delegados - Brindes
    @performance_monitor.measure_time("get_brindes")
    @cache_manager.cache_result(60)
    def get_brindes(self, filial_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém lista de brindes"""
        return self._current_provider.get_brindes(filial_filter)
    
    def get_brinde_by_id(self, brinde_id: int) -> Optional[Dict[str, Any]]:
        """Obtém brinde por ID"""
        return self._current_provider.get_brinde_by_id(brinde_id)
    
    @performance_monitor.measure_time("create_brinde")
    def create_brinde(self, brinde_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo brinde"""
        # Invalidar cache relacionado
        cache_manager.invalidate_cache("get_brindes")
        cache_manager.invalidate_cache("get_estatisticas")
        return self._current_provider.create_brinde(brinde_data)
    
    def update_brinde(self, brinde_id: int, brinde_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza brinde"""
        return self._current_provider.update_brinde(brinde_id, brinde_data)
    
    def delete_brinde(self, brinde_id: int) -> bool:
        """Exclui brinde"""
        return self._current_provider.delete_brinde(brinde_id)
    
    def search_brindes(self, query: str, categoria: str = None, filial: str = None) -> List[Dict[str, Any]]:
        """Busca brindes"""
        return self._current_provider.search_brindes(query, categoria, filial)
    
    # Métodos delegados - Movimentações
    def create_movimentacao(self, movimentacao_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria movimentação"""
        return self._current_provider.create_movimentacao(movimentacao_data)
    
    def get_movimentacoes(self, brinde_id: int = None, tipo: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém movimentações"""
        return self._current_provider.get_movimentacoes(brinde_id, tipo, limit)
    
    def update_estoque_brinde(self, brinde_id: int, quantidade: int, tipo: str) -> bool:
        """Atualiza estoque"""
        return self._current_provider.update_estoque_brinde(brinde_id, quantidade, tipo)

    def find_or_create_brinde_for_transfer(self, brinde_origem: Dict[str, Any], filial_destino: str, username: str) -> Dict[str, Any]:
        """
        Encontra um brinde existente no destino ou cria um novo para a transferência.
        """
        return self._current_provider.find_or_create_brinde_for_transfer(brinde_origem, filial_destino, username)

    # Métodos delegados - Auxiliares
    def get_categorias(self) -> List[str]:
        """Obtém categorias"""
        return self._current_provider.get_categorias()
    
    def get_unidades_medida(self) -> List[str]:
        """Obtém unidades de medida"""
        return self._current_provider.get_unidades_medida()

    def get_filiais(self) -> List[Dict[str, Any]]:
        """Obtém filiais"""
        return self._current_provider.get_filiais()
    
    def get_next_id(self, table: str) -> int:
        """Obtém próximo ID"""
        if hasattr(self._current_provider, 'get_next_id'):
            return self._current_provider.get_next_id(table)
        return 1
    
    def get_next_codigo(self) -> str:
        """Obtém próximo código"""
        if hasattr(self._current_provider, 'get_next_codigo'):
            return self._current_provider.get_next_codigo()
        return "001"
    
    # Métodos específicos para database
    def get_categorias_completas(self) -> List[Dict[str, Any]]:
        """Obtém dados completos das categorias"""
        if self._use_database:
            return self._current_provider.get_categorias_completas()
        else:
            # Para mock, retornar lista simples como dicionários
            categorias = self._current_provider.get_categorias()
            return [{'nome': cat, 'descricao': '', 'id': i+1} for i, cat in enumerate(categorias)]
    
    def get_unidades_medida_completas(self) -> List[Dict[str, Any]]:
        """Obtém dados completos das unidades de medida"""
        if self._use_database:
            return self._current_provider.get_unidades_medida_completas()
        else:
            # Para mock, retornar lista simples como dicionários
            unidades = self._current_provider.get_unidades_medida()
            return [{'codigo': un, 'descricao': f'Descrição {un}', 'id': i+1} for i, un in enumerate(unidades)]
    
    def get_filiais_completas(self) -> List[Dict[str, Any]]:
        """Obtém dados completos das filiais"""
        if self._use_database:
            return self._current_provider.get_filiais_completas()
        else:
            return self._current_provider.data.get('filiais', [])
    
    def get_usuarios_completos(self) -> List[Dict[str, Any]]:
        """Obtém dados completos dos usuários"""
        if self._use_database:
            return self._current_provider.get_usuarios_completos()
        else:
            return self._current_provider.data.get('usuarios', [])
    
    def get_usuario_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtém usuário por username"""
        if self._use_database:
            return self._current_provider.get_usuario_by_username(username)
        else:
            usuarios = self._current_provider.data.get('usuarios', [])
            return next((u for u in usuarios if u.get('username') == username), None)
    
    # Métodos para estatísticas
    def get_estatisticas_dashboard(self) -> Dict[str, Any]:
        """Obtém estatísticas para dashboard"""
        if self._use_database:
            return self._current_provider.get_estatisticas_dashboard()
        else:
            # Calcular estatísticas do mock
            brindes = self.get_brindes()
            total_itens = sum(b.get('quantidade', 0) for b in brindes)
            total_categorias = len(self.get_categorias())
            valor_total = sum(b.get('quantidade', 0) * b.get('valor_unitario', 0) for b in brindes)
            estoque_minimo = self.get_configuracao('estoque_minimo', 10)
            itens_baixo = len([b for b in brindes if b.get('quantidade', 0) <= estoque_minimo])
            
            return {
                'total_itens': total_itens,
                'total_categorias': total_categorias,
                'valor_total': valor_total,
                'itens_estoque_baixo': itens_baixo,
                'estoque_minimo': estoque_minimo
            }
    
    # Métodos CRUD - Categorias
    @performance_monitor.measure_time("create_categoria")
    def create_categoria(self, categoria_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova categoria"""
        cache_manager.invalidate_cache("get_categorias")
        if self._use_database:
            return self._current_provider.create_categoria(categoria_data)
        else:
            # Para mock, simular criação
            if 'categorias' not in self._current_provider.data:
                self._current_provider.data['categorias'] = []
            
            categoria = {
                'id': len(self._current_provider.data['categorias']) + 1,
                'nome': categoria_data.get('nome'),
                'descricao': categoria_data.get('descricao', ''),
                **categoria_data
            }
            self._current_provider.data['categorias'].append(categoria)
            self._current_provider.save_data()
            return categoria
    
    @performance_monitor.measure_time("update_categoria")
    def update_categoria(self, categoria_id: int, categoria_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza categoria"""
        cache_manager.invalidate_cache("get_categorias")
        if self._use_database:
            return self._current_provider.update_categoria(categoria_id, categoria_data)
        else:
            # Para mock, simular atualização
            if 'categorias' not in self._current_provider.data:
                return None
            
            for i, cat in enumerate(self._current_provider.data['categorias']):
                if cat.get('id') == categoria_id:
                    self._current_provider.data['categorias'][i].update(categoria_data)
                    self._current_provider.save_data()
                    return self._current_provider.data['categorias'][i]
            return None
    
    @performance_monitor.measure_time("delete_categoria")
    def delete_categoria(self, categoria_id: int) -> bool:
        """Exclui categoria"""
        cache_manager.invalidate_cache("get_categorias")
        if self._use_database:
            return self._current_provider.delete_categoria(categoria_id)
        else:
            # Para mock, simular exclusão
            if 'categorias' not in self._current_provider.data:
                return False
            
            for i, cat in enumerate(self._current_provider.data['categorias']):
                if cat.get('id') == categoria_id:
                    del self._current_provider.data['categorias'][i]
                    self._current_provider.save_data()
                    return True
            return False
    
    # Métodos CRUD - Unidades de Medida
    @performance_monitor.measure_time("create_unidade_medida")
    def create_unidade_medida(self, unidade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova unidade de medida"""
        cache_manager.invalidate_cache("get_unidades_medida")
        if self._use_database:
            return self._current_provider.create_unidade_medida(unidade_data)
        else:
            # Para mock, simular criação
            if 'unidades_medida' not in self._current_provider.data:
                self._current_provider.data['unidades_medida'] = []
            
            unidade = {
                'id': len(self._current_provider.data['unidades_medida']) + 1,
                'codigo': unidade_data.get('codigo'),
                'descricao': unidade_data.get('descricao'),
                **unidade_data
            }
            self._current_provider.data['unidades_medida'].append(unidade)
            self._current_provider.save_data()
            return unidade
    
    @performance_monitor.measure_time("update_unidade_medida")
    def update_unidade_medida(self, unidade_id: int, unidade_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza unidade de medida"""
        cache_manager.invalidate_cache("get_unidades_medida")
        if self._use_database:
            return self._current_provider.update_unidade_medida(unidade_id, unidade_data)
        else:
            # Para mock, simular atualização
            if 'unidades_medida' not in self._current_provider.data:
                return None
            
            for i, un in enumerate(self._current_provider.data['unidades_medida']):
                if un.get('id') == unidade_id:
                    self._current_provider.data['unidades_medida'][i].update(unidade_data)
                    self._current_provider.save_data()
                    return self._current_provider.data['unidades_medida'][i]
            return None
    
    @performance_monitor.measure_time("delete_unidade_medida")
    def delete_unidade_medida(self, unidade_id: int) -> bool:
        """Exclui unidade de medida"""
        cache_manager.invalidate_cache("get_unidades_medida")
        if self._use_database:
            return self._current_provider.delete_unidade_medida(unidade_id)
        else:
            # Para mock, simular exclusão
            if 'unidades_medida' not in self._current_provider.data:
                return False
            
            for i, un in enumerate(self._current_provider.data['unidades_medida']):
                if un.get('id') == unidade_id:
                    del self._current_provider.data['unidades_medida'][i]
                    self._current_provider.save_data()
                    return True
            return False
    
    # Métodos CRUD - Usuários
    @performance_monitor.measure_time("create_usuario")
    def create_usuario(self, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria novo usuário"""
        cache_manager.invalidate_cache("get_usuarios")
        if self._use_database:
            return self._current_provider.create_usuario(usuario_data)
        else:
            # Para mock, simular criação
            if 'usuarios' not in self._current_provider.data:
                self._current_provider.data['usuarios'] = []
            
            usuario = {
                'id': len(self._current_provider.data['usuarios']) + 1,
                'username': usuario_data.get('username'),
                'nome': usuario_data.get('nome'),
                'email': usuario_data.get('email', ''),
                'filial': usuario_data.get('filial'),
                'perfil': usuario_data.get('perfil'),
                'ativo': usuario_data.get('ativo', True),
                **usuario_data
            }
            self._current_provider.data['usuarios'].append(usuario)
            self._current_provider.save_data()
            return usuario
    
    @performance_monitor.measure_time("update_usuario")
    def update_usuario(self, usuario_id: int, usuario_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza usuário"""
        cache_manager.invalidate_cache("get_usuarios")
        if self._use_database:
            return self._current_provider.update_usuario(usuario_id, usuario_data)
        else:
            # Para mock, simular atualização
            if 'usuarios' not in self._current_provider.data:
                return None
            
            for i, user in enumerate(self._current_provider.data['usuarios']):
                if user.get('id') == usuario_id:
                    self._current_provider.data['usuarios'][i].update(usuario_data)
                    self._current_provider.save_data()
                    return self._current_provider.data['usuarios'][i]
            return None
    
    @performance_monitor.measure_time("get_usuarios")
    @cache_manager.cache_result(60)
    def get_usuarios(self) -> List[Dict[str, Any]]:
        """Obtém lista de usuários"""
        if self._use_database:
            return self._current_provider.get_usuarios()
        else:
            return self._current_provider.data.get('usuarios', [])
    
    # Métodos CRUD - Filiais
    @performance_monitor.measure_time("create_filial")
    def create_filial(self, filial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria nova filial"""
        cache_manager.invalidate_cache("get_filiais")
        if self._use_database:
            return self._current_provider.create_filial(filial_data)
        else:
            # Para mock, simular criação
            if 'filiais' not in self._current_provider.data:
                self._current_provider.data['filiais'] = []
            
            filial = {
                'id': len(self._current_provider.data['filiais']) + 1,
                'numero': filial_data.get('numero'),
                'nome': filial_data.get('nome'),
                'endereco': filial_data.get('endereco', ''),
                'cidade': filial_data.get('cidade'),
                'telefone': filial_data.get('telefone', ''),
                'ativa': filial_data.get('ativa', True),
                **filial_data
            }
            self._current_provider.data['filiais'].append(filial)
            self._current_provider.save_data()
            return filial
    
    @performance_monitor.measure_time("update_filial")
    def update_filial(self, filial_id: int, filial_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza filial"""
        cache_manager.invalidate_cache("get_filiais")
        if self._use_database:
            return self._current_provider.update_filial(filial_id, filial_data)
        else:
            # Para mock, simular atualização
            if 'filiais' not in self._current_provider.data:
                return None
            
            for i, fil in enumerate(self._current_provider.data['filiais']):
                if fil.get('id') == filial_id:
                    self._current_provider.data['filiais'][i].update(filial_data)
                    self._current_provider.save_data()
                    return self._current_provider.data['filiais'][i]
            return None
    
    # Métodos de backup e manutenção
    def backup_data(self, backup_path: str = None) -> str:
        """Cria backup dos dados"""
        if self._use_database:
            from ..database.schema import db_schema
            return db_schema.backup_database(backup_path)
        else:
            # Para mock, copiar arquivo JSON
            import shutil
            from datetime import datetime
            
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_mock_{timestamp}.json"
            
            shutil.copy2(self._current_provider.data_file, backup_path)
            return backup_path
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provedor atual"""
        return {
            'type': 'Database' if self._use_database else 'Mock',
            'provider': type(self._current_provider).__name__,
            'database_available': self._should_use_database()
        }

# Instância global do provedor
data_provider = DataProvider()
