"""
Schema do banco de dados SQLite
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

class DatabaseSchema:
    """Classe para gerenciar o schema do banco de dados"""
    
    def __init__(self, db_path: str = "brindez.db"):
        """Inicializa o schema do banco"""
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Garante que o banco de dados existe e está atualizado"""
        if not os.path.exists(self.db_path):
            self.create_database()
        else:
            self.update_database_if_needed()
    
    def create_database(self):
        """Cria o banco de dados com todas as tabelas"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Habilitar foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Criar todas as tabelas
            self.create_tables(conn)
            
            # Inserir dados iniciais
            self.insert_initial_data(conn)
            
            conn.commit()
            print(f"Banco de dados criado: {self.db_path}")
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao criar banco de dados: {e}")
        finally:
            conn.close()
    
    def create_tables(self, conn: sqlite3.Connection):
        """Cria todas as tabelas do sistema"""
        
        # Tabela de configurações
        conn.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descricao TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de filiais
        conn.execute("""
            CREATE TABLE IF NOT EXISTS filiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                cidade TEXT NOT NULL,
                endereco TEXT,
                telefone TEXT,
                email TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserir filial padrão se não existir
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM filiais")
        if cursor.fetchone()[0] == 0:
            filiais_iniciais = [
                ('001', 'Matriz', 'Cidade Principal', 'Rua Principal, 100', '(00) 1234-5678', 'matriz@empresa.com'),
                ('002', 'Filial 1', 'Cidade Secundária', 'Avenida Central, 200', '(00) 8765-4321', 'filial1@empresa.com'),
                ('003', 'Filial 2', 'Cidade Terciária', 'Alameda das Flores, 300', '(00) 5555-1234', 'filial2@empresa.com')
            ]
            for num, nome, cidade, endereco, telefone, email in filiais_iniciais:
                cursor.execute(
                    """
                    INSERT INTO filiais (numero, nome, cidade, endereco, telefone, email, ativo)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (num, nome, cidade, endereco, telefone, email)
                )
        
        # Tabela de usuários
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                email TEXT,
                filial_id INTEGER NOT NULL,
                perfil TEXT NOT NULL CHECK (perfil IN ('Admin', 'Gestor', 'Usuario')),
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (filial_id) REFERENCES filiais (id)
            )
        """)
        
        # Tabela de categorias
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de unidades de medida
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unidades_medida (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                ativo BOOLEAN DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de fornecedores
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                contato_nome TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                cep TEXT,
                cnpj TEXT,
                observacoes TEXT,
                ativo BOOLEAN DEFAULT 1,
                usuario_criacao_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_criacao_id) REFERENCES usuarios (id)
            )
        """)

        # Tabela de brindes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brindes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                categoria_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0,
                valor_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                unidade_medida_id INTEGER NOT NULL,
                filial_id INTEGER NOT NULL,
                fornecedor_id INTEGER,
                observacoes TEXT,
                ativo BOOLEAN DEFAULT 1,
                usuario_criacao_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (unidade_medida_id) REFERENCES unidades_medida (id),
                FOREIGN KEY (filial_id) REFERENCES filiais (id),
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
                FOREIGN KEY (usuario_criacao_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabela de movimentações
        conn.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brinde_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida', 'transferencia_saida', 'transferencia_entrada')),
                quantidade INTEGER NOT NULL,
                valor_unitario_anterior DECIMAL(10,2),
                valor_unitario_novo DECIMAL(10,2),
                justificativa TEXT,
                observacoes TEXT,
                destino TEXT,
                filial_origem_id INTEGER,
                filial_destino_id INTEGER,
                usuario_id INTEGER NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brinde_id) REFERENCES brindes (id),
                FOREIGN KEY (filial_origem_id) REFERENCES filiais (id),
                FOREIGN KEY (filial_destino_id) REFERENCES filiais (id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        # Tabela de logs de auditoria
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs_auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabela TEXT NOT NULL,
                registro_id INTEGER,
                acao TEXT NOT NULL CHECK (acao IN ('INSERT', 'UPDATE', 'DELETE')),
                dados_anteriores TEXT,
                dados_novos TEXT,
                usuario_id INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        """)
        
        # Índices para melhorar performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fornecedores_codigo ON fornecedores (codigo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fornecedores_nome ON fornecedores (nome)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_fornecedores_ativo ON fornecedores (ativo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brindes_categoria ON brindes (categoria_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brindes_filial ON brindes (filial_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brindes_fornecedor ON brindes (fornecedor_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_brindes_codigo ON brindes (codigo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_movimentacoes_brinde ON movimentacoes (brinde_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_movimentacoes_data ON movimentacoes (data_hora)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_movimentacoes_tipo ON movimentacoes (tipo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios (username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_tabela ON logs_auditoria (tabela, registro_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_data ON logs_auditoria (data_hora)")
    
    def insert_initial_data(self, conn: sqlite3.Connection):
        """Insere dados iniciais no banco"""
        
        # Configurações iniciais
        configuracoes_iniciais = [
            ('estoque_minimo', '10', 'Quantidade mínima para alerta de estoque baixo'),
            ('versao_bd', '1.0', 'Versão do banco de dados'),
            ('backup_automatico', 'true', 'Realizar backup automático'),
            ('intervalo_backup', '24', 'Intervalo de backup em horas')
        ]
        
        for chave, valor, descricao in configuracoes_iniciais:
            conn.execute("""
                INSERT OR IGNORE INTO configuracoes (chave, valor, descricao)
                VALUES (?, ?, ?)
            """, (chave, valor, descricao))
        
        # Filiais iniciais
        filiais_iniciais = [
            ('001', 'Matriz', 'São Paulo', 'Rua Principal, 123', '(11) 1234-5678', 'matriz@empresa.com'),
            ('002', 'Filial São Paulo', 'São Paulo', 'Av. Paulista, 456', '(11) 2345-6789', 'sp@empresa.com'),
            ('003', 'Filial Rio de Janeiro', 'Rio de Janeiro', 'Rua Copacabana, 789', '(21) 3456-7890', 'rj@empresa.com'),
            ('004', 'Filial Belo Horizonte', 'Belo Horizonte', 'Av. Afonso Pena, 321', '(31) 4567-8901', 'bh@empresa.com')
        ]
        
        for numero, nome, cidade, endereco, telefone, email in filiais_iniciais:
            conn.execute("""
                INSERT OR IGNORE INTO filiais (numero, nome, cidade, endereco, telefone, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (numero, nome, cidade, endereco, telefone, email))
        
        # Categorias iniciais
        categorias_iniciais = [
            ('Canetas', 'Canetas e materiais de escrita'),
            ('Chaveiros', 'Chaveiros personalizados'),
            ('Camisetas', 'Camisetas e vestuário'),
            ('Blocos', 'Blocos de anotação e papelaria'),
            ('Eletrônicos', 'Dispositivos eletrônicos'),
            ('Outros', 'Outros itens diversos')
        ]
        
        for nome, descricao in categorias_iniciais:
            conn.execute("""
                INSERT OR IGNORE INTO categorias (nome, descricao)
                VALUES (?, ?)
            """, (nome, descricao))
        
        # Unidades de medida iniciais
        unidades_iniciais = [
            ('UN', 'Unidade'),
            ('KG', 'Quilograma'),
            ('LT', 'Litro'),
            ('CX', 'Caixa'),
            ('PC', 'Peça'),
            ('MT', 'Metro'),
            ('CM', 'Centímetro')
        ]
        
        for codigo, descricao in unidades_iniciais:
            conn.execute("""
                INSERT OR IGNORE INTO unidades_medida (codigo, descricao)
                VALUES (?, ?)
            """, (codigo, descricao))
        
        # Fornecedores iniciais
        fornecedores_iniciais = [
            ('FOR001', 'Brindes & Cia', 'João Silva', '(11) 3333-4444', 'contato@brindesecia.com.br', 
             'Rua das Flores, 123', 'São Paulo', 'SP', '01234-567', '12.345.678/0001-90', 'Fornecedor principal de brindes'),
            ('FOR002', 'Papelaria Central', 'Maria Santos', '(11) 5555-6666', 'vendas@papelcentral.com.br',
             'Av. Central, 456', 'São Paulo', 'SP', '01234-890', '98.765.432/0001-10', 'Especializada em papelaria'),
            ('FOR003', 'Tech Brindes', 'Carlos Oliveira', '(21) 7777-8888', 'info@techbrindes.com.br',
             'Rua da Tecnologia, 789', 'Rio de Janeiro', 'RJ', '20123-456', '11.222.333/0001-44', 'Eletrônicos e gadgets')
        ]
        
        for codigo, nome, contato_nome, telefone, email, endereco, cidade, estado, cep, cnpj, observacoes in fornecedores_iniciais:
            conn.execute("""
                INSERT OR IGNORE INTO fornecedores (codigo, nome, contato_nome, telefone, email, endereco, cidade, estado, cep, cnpj, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (codigo, nome, contato_nome, telefone, email, endereco, cidade, estado, cep, cnpj, observacoes))

        # Usuário admin inicial
        conn.execute("""
            INSERT OR IGNORE INTO usuarios (username, nome, email, filial_id, perfil)
            VALUES ('admin', 'Administrador', 'admin@empresa.com', 1, 'Admin')
        """)
    
    def update_database_if_needed(self):
        """Atualiza o banco de dados se necessário"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Verificar se a tabela fornecedores existe
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='fornecedores'
            """)
            
            if not cursor.fetchone():
                print("Tabela fornecedores não encontrada. Recriando banco...")
                conn.close()
                # Fazer backup do banco atual
                if os.path.exists(self.db_path):
                    backup_path = f"{self.db_path}.backup"
                    os.rename(self.db_path, backup_path)
                    print(f"Backup criado: {backup_path}")
                
                # Recriar banco
                self.create_database()
                return
            
            # Garantir que todas as tabelas existem
            self.create_tables(conn)
            self.insert_initial_data(conn)
            conn.commit()
        except Exception as e:
            print(f"Erro ao atualizar banco: {e}")
            conn.rollback()
        finally:
            if not conn.in_transaction:
                conn.close()
    
    def migrate_to_v1_0(self, conn: sqlite3.Connection):
        """Migração para versão 1.0"""
        # Implementar migrações futuras aqui
        pass
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return conn
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """Executa uma query SELECT e retorna os resultados"""
        conn = self.get_connection()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Executa uma query UPDATE/INSERT/DELETE e retorna o número de linhas afetadas"""
        conn = self.get_connection()
        try:
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Cria um backup do banco de dados"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_brindez_{timestamp}.db"
        
        source_conn = sqlite3.connect(self.db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        try:
            source_conn.backup(backup_conn)
            return backup_path
        finally:
            source_conn.close()
            backup_conn.close()

# Instância global do schema
db_schema = DatabaseSchema()
