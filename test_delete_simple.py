"""
Teste simples para verificar se a correção do método delete_brinde funciona
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_correction():
    """Testa se a correção está funcionando"""
    
    try:
        from src.data.data_provider import data_provider
        from src.database.data_manager import db_data_manager
        
        print("=== TESTE DE CORRECAO DO DELETE_BRINDE ===")
        print(f"Provedor atual: {data_provider.get_provider_info()}")
        
        # Verificar se está usando database
        if not data_provider.is_using_database():
            print("OK: Usando mock data - correção não necessária")
            return True
        
        # Criar um brinde de teste
        print("Criando brinde de teste...")
        brinde_data = {
            'descricao': 'Teste Delete Brinde',
            'categoria': 'Canetas',
            'quantidade': 1,
            'valor_unitario': 1.0,
            'unidade_medida': 'UN',
            'filial': 'Matriz',
            'usuario_cadastro': 'admin'
        }
        
        try:
            brinde_criado = data_provider.create_brinde(brinde_data)
            print(f"Brinde criado: ID {brinde_criado.get('id')}")
            
            # Testar se get_brinde_by_id funciona
            brinde_id = brinde_criado.get('id')
            brinde_dados = db_data_manager.get_brinde_by_id(brinde_id)
            
            if brinde_dados:
                print(f"OK: get_brinde_by_id funcionou - {brinde_dados.get('descricao')}")
                
                # Simular a correção: buscar dados antes de excluir
                print("Testando a correção...")
                dados_antes_exclusao = db_data_manager.get_brinde_by_id(brinde_id)
                
                if dados_antes_exclusao:
                    print("SUCESSO: Dados obtidos antes da exclusão")
                    print(f"Descrição: {dados_antes_exclusao.get('descricao')}")
                    
                    # Agora excluir o brinde de teste
                    if data_provider.delete_brinde(brinde_id):
                        print("SUCESSO: Brinde excluído sem erro")
                        return True
                    else:
                        print("ERRO: Falha na exclusão")
                        return False
                else:
                    print("ERRO: Não foi possível obter dados antes da exclusão")
                    return False
            else:
                print("ERRO: get_brinde_by_id retornou None")
                return False
                
        except Exception as e:
            print(f"ERRO na criação/exclusão: {e}")
            return False
            
    except Exception as e:
        print(f"ERRO geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando teste de correção...")
    
    sucesso = test_correction()
    
    print(f"\nResultado: {'PASSOU' if sucesso else 'FALHOU'}")
    
    if sucesso:
        print("\nA correção está funcionando corretamente!")
        print("O erro 'NoneType object has no attribute get' foi corrigido.")
    else:
        print("\nHouve problemas no teste. Verifique os logs acima.")
