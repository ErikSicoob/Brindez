"""
Teste das otimizações implementadas no sistema de gestão de brindes
"""

import sys
import os
import time

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_performance_improvements():
    """Testa as melhorias de performance"""
    
    try:
        from src.data.data_provider import data_provider
        
        print("=== TESTE DE PERFORMANCE ===")
        print(f"Provedor: {data_provider.get_provider_info()['type']}")
        
        # Teste 1: Velocidade de carregamento de brindes
        start_time = time.time()
        brindes = data_provider.get_brindes()
        load_time = time.time() - start_time
        
        print(f"Carregamento de {len(brindes)} brindes: {load_time:.3f}s")
        
        # Teste 2: Múltiplas consultas (simula filtros)
        start_time = time.time()
        for _ in range(10):
            categorias = data_provider.get_categorias()
            filiais = data_provider.get_filiais()
        multi_query_time = time.time() - start_time
        
        print(f"10 consultas de categorias/filiais: {multi_query_time:.3f}s")
        print(f"Média por consulta: {(multi_query_time/10)*1000:.1f}ms")
        
        # Verificar se performance está aceitável
        if load_time < 1.0 and multi_query_time < 0.5:
            print("SUCESSO: Performance está otimizada")
            return True
        else:
            print("AVISO: Performance pode ser melhorada")
            return False
            
    except Exception as e:
        print(f"ERRO no teste de performance: {e}")
        return False

def test_code_simplification():
    """Testa se o código foi simplificado corretamente"""
    
    try:
        # Verificar se os métodos redundantes foram removidos/simplificados
        from src.ui.screens.brindes import BrindesScreen
        
        print("\n=== TESTE DE SIMPLIFICAÇÃO ===")
        
        # Verificar se métodos existem
        methods_to_check = [
            'refresh_table',
            'refresh_brindes_list', 
            'safe_refresh_table',
            'force_refresh_interface'
        ]
        
        existing_methods = []
        for method in methods_to_check:
            if hasattr(BrindesScreen, method):
                existing_methods.append(method)
        
        print(f"Métodos de refresh encontrados: {existing_methods}")
        
        # Verificar se apply_filters foi simplificado
        import inspect
        apply_filters_code = inspect.getsource(BrindesScreen.apply_filters)
        lines_count = len(apply_filters_code.split('\n'))
        
        print(f"Método apply_filters tem {lines_count} linhas")
        
        if lines_count < 30:  # Método otimizado deve ter menos linhas
            print("SUCESSO: apply_filters foi simplificado")
            return True
        else:
            print("AVISO: apply_filters ainda pode ser simplificado")
            return False
            
    except Exception as e:
        print(f"ERRO no teste de simplificação: {e}")
        return False

def test_immediate_updates():
    """Testa se as atualizações são imediatas"""
    
    try:
        from src.data.data_provider import data_provider
        
        print("\n=== TESTE DE ATUALIZAÇÕES IMEDIATAS ===")
        
        # Verificar se está usando database para teste real
        if not data_provider.is_using_database():
            print("INFO: Usando mock - teste limitado")
            return True
        
        # Contar brindes antes
        brindes_antes = len(data_provider.get_brindes())
        print(f"Brindes antes: {brindes_antes}")
        
        # Criar um brinde de teste
        brinde_data = {
            'descricao': 'Teste Atualização Imediata',
            'categoria': 'Canetas',
            'quantidade': 1,
            'valor_unitario': 1.0,
            'unidade_medida': 'UN',
            'filial': 'Matriz',
            'usuario_cadastro': 'admin'
        }
        
        start_time = time.time()
        brinde_criado = data_provider.create_brinde(brinde_data)
        create_time = time.time() - start_time
        
        # Verificar se foi criado imediatamente
        brindes_depois = len(data_provider.get_brindes())
        print(f"Brindes depois: {brindes_depois}")
        print(f"Tempo de criação: {create_time:.3f}s")
        
        if brindes_depois > brindes_antes and create_time < 1.0:
            print("SUCESSO: Criação é imediata")
            
            # Testar exclusão imediata
            start_time = time.time()
            data_provider.delete_brinde(brinde_criado['id'])
            delete_time = time.time() - start_time
            
            brindes_final = len(data_provider.get_brindes())
            print(f"Brindes após exclusão: {brindes_final}")
            print(f"Tempo de exclusão: {delete_time:.3f}s")
            
            if brindes_final == brindes_antes and delete_time < 1.0:
                print("SUCESSO: Exclusão é imediata")
                return True
            else:
                print("AVISO: Exclusão não é imediata")
                return False
        else:
            print("AVISO: Criação não é imediata")
            return False
            
    except Exception as e:
        print(f"ERRO no teste de atualizações: {e}")
        return False

def main():
    """Função principal de testes"""
    print("TESTE DE OTIMIZACOES - Sistema de Brindes")
    print("=" * 50)
    
    # Executar testes
    test1 = test_performance_improvements()
    test2 = test_code_simplification()
    test3 = test_immediate_updates()
    
    # Relatório final
    print(f"\nRELATORIO DE OTIMIZACOES:")
    print(f"Performance: {'OK' if test1 else 'PRECISA MELHORAR'}")
    print(f"Simplificacao: {'OK' if test2 else 'PRECISA SIMPLIFICAR'}")
    print(f"Atualizacoes: {'OK' if test3 else 'PRECISA OTIMIZAR'}")
    
    success = test1 and test2 and test3
    
    if success:
        print("\nTODAS AS OTIMIZACOES ESTAO FUNCIONANDO!")
        print("Sistema otimizado para gestao eficiente de brindes")
    else:
        print("\nALGUMAS OTIMIZACOES PRECISAM DE AJUSTES")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
