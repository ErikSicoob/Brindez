#!/usr/bin/env python3
"""
Script para recriar o banco de dados com a tabela fornecedores
"""

import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.schema import DatabaseSchema

def recreate_database():
    """Recria o banco de dados"""
    db_path = "brindez.db"
    
    # Fazer backup se existir
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup"
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(db_path, backup_path)
        print(f"Backup criado: {backup_path}")
    
    # Recriar banco
    print("Recriando banco de dados...")
    schema = DatabaseSchema(db_path)
    print("Banco de dados recriado com sucesso!")
    
    # Verificar se a tabela fornecedores foi criada
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fornecedores'")
    if cursor.fetchone():
        print("OK: Tabela 'fornecedores' criada com sucesso!")
    else:
        print("ERRO: Tabela 'fornecedores' não foi criada!")
    
    # Verificar dados iniciais
    cursor = conn.execute("SELECT COUNT(*) FROM fornecedores")
    count = cursor.fetchone()[0]
    print(f"OK: {count} fornecedores iniciais inseridos")
    
    conn.close()

if __name__ == "__main__":
    recreate_database()
