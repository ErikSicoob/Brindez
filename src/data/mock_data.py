"""
Gerenciador de dados mock para desenvolvimento
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class MockDataManager:
    """Classe para gerenciar dados mock durante o desenvolvimento"""
    
    def __init__(self):
        """Inicializa o gerenciador de dados mock"""
        self.data_file = "mock_data.json"
        self.data = self.load_data()
        
    def load_data(self) -> Dict[str, Any]:
        """Carrega dados do arquivo JSON ou cria dados iniciais"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Dados iniciais se arquivo não existe
        return self.create_initial_data()
    
    def save_data(self):
        """Salva dados no arquivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")
    
    def create_initial_data(self) -> Dict[str, Any]:
        """Cria dados iniciais para o sistema"""
        return {
            "brindes": [
                {
                    "id": 1,
                    "codigo": "001",
                    "descricao": "Caneta Azul BIC",
                    "categoria": "Canetas",
                    "quantidade": 150,
                    "valor_unitario": 2.50,
                    "unidade_medida": "UN",
                    "filial": "Matriz",
                    "data_cadastro": "2025-09-20T10:00:00",
                    "usuario_cadastro": "admin"
                },
                {
                    "id": 2,
                    "codigo": "002",
                    "descricao": "Chaveiro Metálico",
                    "categoria": "Chaveiros",
                    "quantidade": 75,
                    "valor_unitario": 8.00,
                    "unidade_medida": "UN",
                    "filial": "Matriz",
                    "data_cadastro": "2025-09-20T11:00:00",
                    "usuario_cadastro": "admin"
                },
                {
                    "id": 3,
                    "codigo": "003",
                    "descricao": "Camiseta Polo P",
                    "categoria": "Camisetas",
                    "quantidade": 25,
                    "valor_unitario": 35.00,
                    "unidade_medida": "UN",
                    "filial": "Filial SP",
                    "data_cadastro": "2025-09-21T09:00:00",
                    "usuario_cadastro": "joao.silva"
                },
                {
                    "id": 4,
                    "codigo": "004",
                    "descricao": "Bloco A4 50 folhas",
                    "categoria": "Blocos",
                    "quantidade": 200,
                    "valor_unitario": 12.00,
                    "unidade_medida": "UN",
                    "filial": "Matriz",
                    "data_cadastro": "2025-09-21T14:00:00",
                    "usuario_cadastro": "admin"
                },
                {
                    "id": 5,
                    "codigo": "005",
                    "descricao": "Caneta Gel Preta",
                    "categoria": "Canetas",
                    "quantidade": 5,
                    "valor_unitario": 4.50,
                    "unidade_medida": "UN",
                    "filial": "Filial RJ",
                    "data_cadastro": "2025-09-22T08:00:00",
                    "usuario_cadastro": "maria.santos"
                }
            ],
            "categorias": [
                {"id": 1, "nome": "Canetas", "ativo": True},
                {"id": 2, "nome": "Chaveiros", "ativo": True},
                {"id": 3, "nome": "Camisetas", "ativo": True},
                {"id": 4, "nome": "Blocos", "ativo": True},
                {"id": 5, "nome": "Eletrônicos", "ativo": True},
                {"id": 6, "nome": "Outros", "ativo": True}
            ],
            "unidades_medida": [
                {"id": 1, "codigo": "UN", "descricao": "Unidade", "ativo": True},
                {"id": 2, "codigo": "KG", "descricao": "Quilograma", "ativo": True},
                {"id": 3, "codigo": "LT", "descricao": "Litro", "ativo": True},
                {"id": 4, "codigo": "CX", "descricao": "Caixa", "ativo": True},
                {"id": 5, "codigo": "PC", "descricao": "Peça", "ativo": True}
            ],
            "filiais": [
                {"id": 1, "numero": "001", "nome": "Matriz", "cidade": "São Paulo", "ativo": True},
                {"id": 2, "numero": "002", "nome": "Filial São Paulo", "cidade": "São Paulo", "ativo": True},
                {"id": 3, "numero": "003", "nome": "Filial Rio de Janeiro", "cidade": "Rio de Janeiro", "ativo": True},
                {"id": 4, "numero": "004", "nome": "Filial Belo Horizonte", "cidade": "Belo Horizonte", "ativo": True}
            ],
            "movimentacoes": [],
            "usuarios": [
                {"id": 1, "username": "admin", "nome": "Administrador", "filial": "Matriz", "perfil": "Admin", "ativo": True},
                {"id": 2, "username": "joao.silva", "nome": "João Silva", "filial": "Filial SP", "perfil": "Gestor", "ativo": True},
                {"id": 3, "username": "maria.santos", "nome": "Maria Santos", "filial": "Filial RJ", "perfil": "Usuario", "ativo": True}
            ],
            "configuracoes": {
                "estoque_minimo": 10,
                "caminho_bd": "brindez.db"
            }
        }
    
    def get_next_id(self, table: str) -> int:
        """Obtém o próximo ID para uma tabela"""
        if table not in self.data:
            return 1
        
        items = self.data[table]
        if not items:
            return 1
        
        return max(item.get('id', 0) for item in items) + 1
    
    def get_next_codigo(self) -> str:
        """Obtém o próximo código para brindes"""
        brindes = self.data.get('brindes', [])
        if not brindes:
            return "001"
        
        codigos = [int(brinde.get('codigo', '0')) for brinde in brindes if brinde.get('codigo', '').isdigit()]
        if not codigos:
            return "001"
        
        return f"{max(codigos) + 1:03d}"
    
    # CRUD para Brindes
    def get_brindes(self, filial_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém lista de brindes"""
        brindes = self.data.get('brindes', [])
        
        if filial_filter and filial_filter != "Todas":
            brindes = [b for b in brindes if b.get('filial') == filial_filter]
        
        return brindes
    
    def get_brinde_by_id(self, brinde_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um brinde por ID"""
        brindes = self.data.get('brindes', [])
        return next((b for b in brindes if b.get('id') == brinde_id), None)
    
    def create_brinde(self, brinde_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria um novo brinde"""
        if 'brindes' not in self.data:
            self.data['brindes'] = []
        
        # Gerar ID e código
        brinde_data['id'] = self.get_next_id('brindes')
        if not brinde_data.get('codigo'):
            brinde_data['codigo'] = self.get_next_codigo()
        
        # Adicionar timestamps
        brinde_data['data_cadastro'] = datetime.now().isoformat()
        
        # Converter valores numéricos
        if 'quantidade' in brinde_data:
            brinde_data['quantidade'] = int(brinde_data['quantidade'])
        if 'valor_unitario' in brinde_data:
            brinde_data['valor_unitario'] = float(str(brinde_data['valor_unitario']).replace(',', '.'))
        
        self.data['brindes'].append(brinde_data)
        self.save_data()
        
        return brinde_data
    
    def update_brinde(self, brinde_id: int, brinde_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Atualiza um brinde"""
        brindes = self.data.get('brindes', [])
        
        for i, brinde in enumerate(brindes):
            if brinde.get('id') == brinde_id:
                # Preparar dados para atualização
                update_payload = brinde_data.copy()

                # Adicionar timestamp de atualização
                update_payload['data_atualizacao'] = datetime.now().isoformat()
                
                # Converter valores numéricos
                if 'quantidade' in update_payload:
                    update_payload['quantidade'] = int(update_payload['quantidade'])
                if 'valor_unitario' in update_payload:
                    update_payload['valor_unitario'] = float(str(update_payload['valor_unitario']).replace(',', '.'))
                
                # Atualizar o dicionário existente em vez de substituí-lo
                self.data['brindes'][i].update(update_payload)
                self.save_data()
                return self.data['brindes'][i]
        
        return None
    
    def delete_brinde(self, brinde_id: int) -> bool:
        """Exclui um brinde"""
        brindes = self.data.get('brindes', [])
        
        for i, brinde in enumerate(brindes):
            if brinde.get('id') == brinde_id:
                del self.data['brindes'][i]
                self.save_data()
                return True
        
        return False
    
    # CRUD para Movimentações
    def create_movimentacao(self, movimentacao_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria uma nova movimentação"""
        if 'movimentacoes' not in self.data:
            self.data['movimentacoes'] = []
        
        # Gerar ID
        movimentacao_data['id'] = self.get_next_id('movimentacoes')
        
        # Adicionar timestamp
        movimentacao_data['data_hora'] = datetime.now().isoformat()
        
        # Converter quantidade
        if 'quantidade' in movimentacao_data:
            movimentacao_data['quantidade'] = int(movimentacao_data['quantidade'])
        
        # Atualizar estoque do brinde
        brinde_id = movimentacao_data.get('brinde_id')
        quantidade = movimentacao_data.get('quantidade', 0)
        tipo = movimentacao_data.get('tipo', 'entrada')
        
        if brinde_id and self.update_estoque_brinde(brinde_id, quantidade, tipo):
            self.data['movimentacoes'].append(movimentacao_data)
            self.save_data()
            return movimentacao_data
        else:
            raise Exception("Erro ao atualizar estoque do brinde")
    
    def update_estoque_brinde(self, brinde_id: int, quantidade: int, tipo: str) -> bool:
        """Atualiza o estoque de um brinde"""
        brindes = self.data.get('brindes', [])
        
        for brinde in brindes:
            if brinde.get('id') == brinde_id:
                estoque_atual = brinde.get('quantidade', 0)
                
                if tipo == 'entrada':
                    novo_estoque = estoque_atual + quantidade
                elif tipo == 'saida':
                    novo_estoque = estoque_atual - quantidade
                    if novo_estoque < 0:
                        raise Exception("Estoque insuficiente")
                else:
                    return False
                
                brinde['quantidade'] = novo_estoque
                return True
        
        return False
    
    def get_movimentacoes(self, brinde_id: int = None, tipo: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Obtém lista de movimentações"""
        movimentacoes = self.data.get('movimentacoes', [])
        
        # Filtrar por brinde
        if brinde_id:
            movimentacoes = [m for m in movimentacoes if m.get('brinde_id') == brinde_id]
        
        # Filtrar por tipo
        if tipo:
            movimentacoes = [m for m in movimentacoes if m.get('tipo') == tipo]
        
        # Ordenar por data (mais recente primeiro)
        movimentacoes.sort(key=lambda x: x.get('data_hora', ''), reverse=True)
        
        # Limitar resultados
        if limit:
            movimentacoes = movimentacoes[:limit]
        
        return movimentacoes
    
    def find_or_create_brinde_for_transfer(self, brinde_origem: Dict[str, Any], filial_destino: str, username: str) -> Dict[str, Any]:
        """
        Encontra um brinde existente no destino ou cria um novo para a transferência (versão mock).
        """
        # Verificar se já existe um brinde com a mesma descrição na filial de destino
        brindes_destino = self.get_brindes(filial_filter=filial_destino)
        brinde_destino_existente = next((b for b in brindes_destino if b['descricao'] == brinde_origem['descricao']), None)

        if brinde_destino_existente:
            return brinde_destino_existente

        # Se não existir, criar um novo brinde na filial de destino com estoque zero
        else:
            novo_brinde_data = {
                'descricao': brinde_origem['descricao'],
                'categoria': brinde_origem['categoria'],
                'quantidade': 0,  # Começa com zero
                'valor_unitario': brinde_origem['valor_unitario'],
                'unidade_medida': brinde_origem['unidade_medida'],
                'filial': filial_destino,
                'usuario_cadastro': username
            }
            return self.create_brinde(novo_brinde_data)

    # Métodos auxiliares
    def get_categorias(self) -> List[str]:
        """Obtém lista de categorias ativas"""
        categorias = self.data.get('categorias', [])
        return [cat['nome'] for cat in categorias if cat.get('ativo', True)]
    
    def get_unidades_medida(self) -> List[str]:
        """Obtém lista de unidades de medida ativas"""
        unidades = self.data.get('unidades_medida', [])
        return [un['codigo'] for un in unidades if un.get('ativo', True)]
    
    def get_filiais(self) -> List[str]:
        """Obtém lista de filiais ativas"""
        filiais = self.data.get('filiais', [])
        return [fil['nome'] for fil in filiais if fil.get('ativo', True)]
    
    def search_brindes(self, query: str, categoria: str = None, filial: str = None) -> List[Dict[str, Any]]:
        """Busca brindes por critérios"""
        brindes = self.get_brindes(filial)
        
        if query:
            query = query.lower()
            brindes = [
                b for b in brindes 
                if query in b.get('descricao', '').lower() or 
                   query in b.get('codigo', '').lower()
            ]
        
        if categoria and categoria != "Todas":
            brindes = [b for b in brindes if b.get('categoria') == categoria]
        
        return brindes
    
    # Métodos de Fornecedores (Mock)
    def get_fornecedores(self) -> List[Dict[str, Any]]:
        """Retorna lista de fornecedores"""
        # Verificar se já existem fornecedores nos dados
        fornecedores_existentes = self.data.get('fornecedores', [])
        
        # Se não existem, criar dados padrão
        if not fornecedores_existentes:
            fornecedores_padrao = [
                {
                    'id': 1,
                    'codigo': 'FOR001',
                    'nome': 'Brindes & Cia',
                    'contato_nome': 'João Silva',
                    'telefone': '(11) 3333-4444',
                    'email': 'contato@brindesecia.com.br',
                    'endereco': 'Rua das Flores, 123',
                    'cidade': 'São Paulo',
                    'estado': 'SP',
                    'cep': '01234-567',
                    'cnpj': '12.345.678/0001-90',
                    'observacoes': 'Fornecedor principal de brindes',
                    'ativo': True
                },
                {
                    'id': 2,
                    'codigo': 'FOR002',
                    'nome': 'Papelaria Central',
                    'contato_nome': 'Maria Santos',
                    'telefone': '(11) 5555-6666',
                    'email': 'vendas@papelcentral.com.br',
                    'endereco': 'Av. Central, 456',
                    'cidade': 'São Paulo',
                    'estado': 'SP',
                    'cep': '01234-890',
                    'cnpj': '98.765.432/0001-10',
                    'observacoes': 'Especializada em papelaria',
                    'ativo': True
                },
                {
                    'id': 3,
                    'codigo': 'FOR003',
                    'nome': 'Tech Brindes',
                    'contato_nome': 'Carlos Oliveira',
                    'telefone': '(21) 7777-8888',
                    'email': 'info@techbrindes.com.br',
                    'endereco': 'Rua da Tecnologia, 789',
                    'cidade': 'Rio de Janeiro',
                    'estado': 'RJ',
                    'cep': '20123-456',
                    'cnpj': '11.222.333/0001-44',
                    'observacoes': 'Eletrônicos e gadgets',
                    'ativo': True
                }
            ]
            self.data['fornecedores'] = fornecedores_padrao
            self.save_data()
            return fornecedores_padrao
        
        return fornecedores_existentes
    
    def get_fornecedor_by_id(self, fornecedor_id: int) -> Optional[Dict[str, Any]]:
        """Retorna fornecedor por ID"""
        fornecedores = self.get_fornecedores()
        return next((f for f in fornecedores if f['id'] == fornecedor_id), None)
    
    def create_fornecedor(self, data: Dict[str, Any]) -> bool:
        """Cria novo fornecedor (mock)"""
        fornecedores = self.data.get('fornecedores', [])
        
        # Gerar ID automático
        max_id = max([f.get('id', 0) for f in fornecedores], default=0)
        data['id'] = max_id + 1
        
        # Gerar código se não fornecido
        if not data.get('codigo'):
            max_num = 0
            for f in fornecedores:
                codigo = f.get('codigo', '')
                if codigo.startswith('FOR'):
                    try:
                        num = int(codigo[3:])
                        max_num = max(max_num, num)
                    except:
                        pass
            data['codigo'] = f"FOR{max_num + 1:03d}"
        
        data['ativo'] = True
        fornecedores.append(data)
        self.data['fornecedores'] = fornecedores
        self.save_data()
        return True
    
    def update_fornecedor(self, fornecedor_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza fornecedor (mock)"""
        fornecedores = self.data.get('fornecedores', [])
        for i, f in enumerate(fornecedores):
            if f['id'] == fornecedor_id:
                fornecedores[i].update(data)
                self.save_data()
                return True
        return False
    
    def delete_fornecedor(self, fornecedor_id: int) -> bool:
        """Remove fornecedor (mock - soft delete)"""
        return self.update_fornecedor(fornecedor_id, {'ativo': False})
    
    def search_fornecedores(self, termo: str) -> List[Dict[str, Any]]:
        """Busca fornecedores por termo (mock)"""
        fornecedores = self.get_fornecedores()
        if not termo:
            return fornecedores
        
        termo = termo.lower()
        return [
            f for f in fornecedores
            if termo in f.get('nome', '').lower() or
               termo in f.get('codigo', '').lower() or
               termo in f.get('contato_nome', '').lower() or
               termo in f.get('email', '').lower()
        ]

# Instância global do gerenciador
mock_data = MockDataManager()
