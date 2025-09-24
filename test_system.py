"""
Testes automatizados do Sistema de Controle de Brindes
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Adicionar src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.validators import Validators, BrindeValidator, MovimentacaoValidator, ValidationError, BusinessRuleError
from src.data.data_provider import data_provider
from src.utils.user_manager import UserManager
from src.utils.audit_logger import audit_logger

class TestValidators(unittest.TestCase):
    """Testes dos validadores"""
    
    def test_validate_required(self):
        """Testa validação de campos obrigatórios"""
        # Deve passar
        Validators.validate_required("valor", "Campo")
        
        # Deve falhar
        with self.assertRaises(ValidationError):
            Validators.validate_required("", "Campo")
        
        with self.assertRaises(ValidationError):
            Validators.validate_required(None, "Campo")
    
    def test_validate_positive_number(self):
        """Testa validação de números positivos"""
        # Deve passar
        Validators.validate_positive_number("10", "Campo")
        Validators.validate_positive_number("10.5", "Campo")
        Validators.validate_positive_number("10,5", "Campo")
        
        # Deve falhar
        with self.assertRaises(ValidationError):
            Validators.validate_positive_number("0", "Campo")
        
        with self.assertRaises(ValidationError):
            Validators.validate_positive_number("-5", "Campo")
        
        with self.assertRaises(ValidationError):
            Validators.validate_positive_number("abc", "Campo")
    
    def test_validate_email(self):
        """Testa validação de email"""
        # Deve passar
        Validators.validate_email("test@example.com", "Email")
        Validators.validate_email("user.name@domain.com.br", "Email")
        
        # Deve falhar
        with self.assertRaises(ValidationError):
            Validators.validate_email("invalid-email", "Email")
        
        with self.assertRaises(ValidationError):
            Validators.validate_email("@domain.com", "Email")

class TestBrindeValidator(unittest.TestCase):
    """Testes do validador de brindes"""
    
    def setUp(self):
        """Configuração inicial"""
        self.categorias = ["Canetas", "Chaveiros", "Camisetas"]
        self.unidades = ["UN", "KG", "LT"]
        self.filiais = ["Matriz", "Filial SP", "Filial RJ"]
    
    def test_validate_brinde_data_valid(self):
        """Testa validação de dados válidos de brinde"""
        data = {
            'descricao': 'Caneta Azul BIC',
            'categoria': 'Canetas',
            'quantidade': '10',
            'valor_unitario': '2,50',
            'unidade_medida': 'UN',
            'filial': 'Matriz'
        }
        
        result = BrindeValidator.validate_brinde_data(data, self.categorias, self.unidades, self.filiais)
        
        self.assertEqual(result['descricao'], 'Caneta Azul BIC')
        self.assertEqual(result['quantidade'], 10)
        self.assertEqual(result['valor_unitario'], 2.5)
    
    def test_validate_brinde_data_invalid(self):
        """Testa validação de dados inválidos de brinde"""
        # Categoria inválida
        data = {
            'descricao': 'Caneta Azul BIC',
            'categoria': 'Categoria Inexistente',
            'quantidade': '10',
            'valor_unitario': '2,50',
            'unidade_medida': 'UN',
            'filial': 'Matriz'
        }
        
        with self.assertRaises(BusinessRuleError):
            BrindeValidator.validate_brinde_data(data, self.categorias, self.unidades, self.filiais)

class TestDataProvider(unittest.TestCase):
    """Testes do provedor de dados"""
    
    def setUp(self):
        """Configuração inicial"""
        # Forçar uso de mock para testes
        data_provider.switch_to_mock()
    
    def test_get_categorias(self):
        """Testa obtenção de categorias"""
        categorias = data_provider.get_categorias()
        self.assertIsInstance(categorias, list)
        self.assertGreater(len(categorias), 0)
    
    def test_get_filiais(self):
        """Testa obtenção de filiais"""
        filiais = data_provider.get_filiais()
        self.assertIsInstance(filiais, list)
        self.assertGreater(len(filiais), 0)
    
    def test_get_brindes(self):
        """Testa obtenção de brindes"""
        brindes = data_provider.get_brindes()
        self.assertIsInstance(brindes, list)
    
    def test_create_brinde(self):
        """Testa criação de brinde"""
        brinde_data = {
            'descricao': 'Teste Caneta',
            'categoria': 'Canetas',
            'quantidade': 5,
            'valor_unitario': 1.50,
            'unidade_medida': 'UN',
            'filial': 'Matriz',
            'usuario_cadastro': 'admin'
        }
        
        brinde = data_provider.create_brinde(brinde_data)
        
        self.assertIsNotNone(brinde)
        self.assertEqual(brinde['descricao'], 'Teste Caneta')
        self.assertIn('codigo', brinde)
        self.assertIn('id', brinde)

class TestUserManager(unittest.TestCase):
    """Testes do gerenciador de usuários"""
    
    def setUp(self):
        """Configuração inicial"""
        self.user_manager = UserManager()
    
    def test_get_windows_user(self):
        """Testa obtenção do usuário Windows"""
        user = self.user_manager.get_windows_user()
        self.assertIsInstance(user, str)
        self.assertGreater(len(user), 0)
    
    def test_authenticate_user(self):
        """Testa autenticação de usuário"""
        success, message = self.user_manager.authenticate_user()
        self.assertTrue(success)
        self.assertIsInstance(message, str)
    
    def test_get_current_user(self):
        """Testa obtenção do usuário atual"""
        self.user_manager.authenticate_user()
        user = self.user_manager.get_current_user()
        
        self.assertIsNotNone(user)
        self.assertIn('username', user)
        self.assertIn('name', user)
        self.assertIn('profile', user)

class TestSystemIntegration(unittest.TestCase):
    """Testes de integração do sistema"""
    
    def setUp(self):
        """Configuração inicial"""
        data_provider.switch_to_mock()
        self.user_manager = UserManager()
        self.user_manager.authenticate_user()
    
    def test_complete_brinde_workflow(self):
        """Testa fluxo completo de brinde"""
        # 1. Criar brinde
        brinde_data = {
            'descricao': 'Teste Workflow',
            'categoria': 'Canetas',
            'quantidade': 10,
            'valor_unitario': 2.00,
            'unidade_medida': 'UN',
            'filial': 'Matriz',
            'usuario_cadastro': 'admin'
        }
        
        brinde = data_provider.create_brinde(brinde_data)
        self.assertIsNotNone(brinde)
        
        # 2. Atualizar brinde
        brinde_data['descricao'] = 'Teste Workflow Atualizado'
        brinde_data['quantidade'] = 15
        
        brinde_atualizado = data_provider.update_brinde(brinde['id'], brinde_data)
        self.assertIsNotNone(brinde_atualizado)
        self.assertEqual(brinde_atualizado['descricao'], 'Teste Workflow Atualizado')
        
        # 3. Criar movimentação
        movimentacao_data = {
            'brinde_id': brinde['id'],
            'brinde_codigo': brinde['codigo'],
            'brinde_descricao': brinde['descricao'],
            'tipo': 'entrada',
            'quantidade': 5,
            'usuario': 'admin',
            'observacoes': 'Teste de entrada',
            'filial': 'Matriz'
        }
        
        movimentacao = data_provider.create_movimentacao(movimentacao_data)
        self.assertIsNotNone(movimentacao)
        
        # 4. Verificar movimentações
        movimentacoes = data_provider.get_movimentacoes(brinde_id=brinde['id'])
        self.assertGreater(len(movimentacoes), 0)

def run_performance_tests():
    """Executa testes de performance"""
    print("\nExecutando testes de performance...")
    
    import time
    from src.utils.performance import performance_monitor
    
    # Teste de tempo de resposta
    start_time = time.time()
    
    # Simular operações
    for i in range(100):
        data_provider.get_categorias()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"100 consultas de categorias: {total_time:.3f}s")
    print(f"Media por consulta: {(total_time/100)*1000:.1f}ms")
    
    # Obter métricas
    metrics = performance_monitor.get_metrics()
    if metrics:
        print("\nMetricas de performance:")
        for operation, data in metrics.items():
            print(f"  {operation}: {data['avg_time']*1000:.1f}ms avg, {data['total_calls']} calls")

def run_memory_tests():
    """Executa testes de memória"""
    print("\nExecutando testes de memoria...")
    
    try:
        from src.utils.performance import performance_optimizer
        
        memory_info = performance_optimizer.memory_manager.get_memory_usage()
        print(f"Uso de memoria: {memory_info['rss'] / 1024 / 1024:.1f} MB")
        print(f"Percentual: {memory_info['percent']:.1f}%")
        
        # Teste de limpeza
        collected = performance_optimizer.memory_manager.cleanup_unused_objects()
        print(f"Objetos coletados: {collected}")
        
    except Exception as e:
        print(f"Teste de memoria falhou: {e}")

def main():
    """Função principal de testes"""
    print("Sistema de Testes - Controle de Brindes")
    print("=" * 50)
    
    # Configurar ambiente de teste
    os.environ['TESTING'] = '1'
    
    # Executar testes unitários
    print("\nExecutando testes unitarios...")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TestValidators))
    suite.addTests(loader.loadTestsFromTestCase(TestBrindeValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestDataProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestUserManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Executar testes de performance
    run_performance_tests()
    
    # Executar testes de memória
    run_memory_tests()
    
    # Relatório final
    print("\nRelatorio Final:")
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    
    if result.failures:
        print("\nFalhas encontradas:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nErros encontrados:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\nTodos os testes passaram!")
        return True
    else:
        print("\nAlguns testes falharam!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
