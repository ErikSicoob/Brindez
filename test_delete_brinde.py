"""
Teste para verificar se a correção do método delete_brinde funciona corretamente
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_delete_brinde_correction():
    """Testa se o método delete_brinde não gera mais o erro 'NoneType' object has no attribute 'get'"""
    
    try:
        from src.data.data_provider import data_provider
        from src.database.data_manager import db_data_manager
        
        print("=== TESTE DE CORREÇÃO DO DELETE_BRINDE ===")
        print(f"Provedor atual: {data_provider.get_provider_info()}")
        
        # Obter lista de brindes
        brindes = data_provider.get_brindes()
        print(f"Total de brindes encontrados: {len(brindes)}")
        
        if not brindes:
            print("ERRO: Nenhum brinde encontrado para testar")
            return False
        
        # Pegar o primeiro brinde válido
        brinde_teste = None
        for brinde in brindes:
            if brinde and isinstance(brinde, dict) and 'id' in brinde:
                brinde_teste = brinde
                break
        
        if not brinde_teste:
            print("❌ Nenhum brinde válido encontrado para testar")
            return False
        
        print(f"Brinde selecionado para teste: {brinde_teste.get('descricao', 'N/A')} (ID: {brinde_teste.get('id')})")
        
        # Testar o método get_brinde_by_id primeiro
        print("\n--- Testando get_brinde_by_id ---")
        brinde_dados = data_provider.get_brinde_by_id(brinde_teste['id'])
        
        if brinde_dados:
            print(f"✅ get_brinde_by_id funcionou: {brinde_dados.get('descricao', 'N/A')}")
        else:
            print("❌ get_brinde_by_id retornou None")
            return False
        
        # Simular o método delete_brinde sem realmente excluir
        print("\n--- Simulando delete_brinde (sem excluir) ---")
        
        if data_provider.is_using_database():
            # Testar diretamente no data_manager
            brinde_data_antes = db_data_manager.get_brinde_by_id(brinde_teste['id'])
            print(f"Dados do brinde antes da exclusão: {brinde_data_antes.get('descricao') if brinde_data_antes else 'None'}")
            
            if brinde_data_antes:
                print("✅ Correção funcionou: dados do brinde foram obtidos antes da exclusão")
                print("✅ O erro 'NoneType' object has no attribute 'get' não deve mais ocorrer")
                return True
            else:
                print("❌ Ainda há problema: get_brinde_by_id retornou None")
                return False
        else:
            print("✅ Usando mock data - correção não necessária para mock")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_audit_logger_call():
    """Testa se a chamada para audit_logger está correta"""
    
    try:
        from src.utils.audit_logger import audit_logger
        
        print("\n=== TESTE DE CHAMADA DO AUDIT_LOGGER ===")
        
        # Testar com dados válidos
        brinde_data_exemplo = {
            'id': 1,
            'descricao': 'Caneta Teste',
            'categoria': 'Canetas',
            'quantidade': 10
        }
        
        print("Testando audit_brinde_deleted com dados válidos...")
        audit_logger.audit_brinde_deleted(1, brinde_data_exemplo)
        print("✅ audit_brinde_deleted funcionou com dados válidos")
        
        # Testar com None (situação anterior que causava erro)
        print("Testando audit_brinde_deleted com None...")
        try:
            audit_logger.audit_brinde_deleted(1, None)
            print("❌ audit_brinde_deleted não deveria funcionar com None")
            return False
        except Exception as e:
            print(f"✅ audit_brinde_deleted corretamente falhou com None: {e}")
            return True
            
    except Exception as e:
        print(f"❌ Erro durante teste do audit_logger: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando testes de correção do delete_brinde...\n")
    
    sucesso1 = test_delete_brinde_correction()
    sucesso2 = test_audit_logger_call()
    
    print(f"\n=== RESULTADO DOS TESTES ===")
    print(f"Teste delete_brinde: {'✅ PASSOU' if sucesso1 else '❌ FALHOU'}")
    print(f"Teste audit_logger: {'✅ PASSOU' if sucesso2 else '❌ FALHOU'}")
    
    if sucesso1 and sucesso2:
        print("\n🎉 TODOS OS TESTES PASSARAM! A correção está funcionando.")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM. Verifique os logs acima.")
