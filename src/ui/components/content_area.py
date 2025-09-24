"""
Componente da área de conteúdo principal
"""

import customtkinter as ctk
from ..screens.dashboard import DashboardScreen
from ..screens.brindes import BrindesScreen
from ..screens.estoque_brindes import EstoqueBrindesScreen
from ..screens.movimentacoes import MovimentacoesScreen
from ..screens.relatorios import RelatoriosScreen
from ..screens.configuracoes import ConfiguracoesScreen
from ...utils.user_manager import UserManager

class ContentArea:
    """Classe da área de conteúdo principal"""
    
    def __init__(self, parent, current_user):
        """Inicializa a área de conteúdo"""
        self.parent = parent
        self.current_user = current_user
        self.current_screen = None
        
        # Criar frame principal
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Inicializar containers de telas: factories e instâncias (lazy init)
        self.screens = {}
        self.screen_factories = {}
        self.setup_screens()
    
    def setup_screens(self):
        """Configura as fábricas das telas (instancia sob demanda)"""
        # Criar instância do user_manager uma única vez
        user_manager = UserManager()

        # Registrar fábricas (callables) para criação das telas sob demanda
        self.screen_factories = {
            'dashboard': lambda: DashboardScreen(self.frame),
            'brindes': lambda: BrindesScreen(self.frame, user_manager),
            'estoque_brindes': lambda: EstoqueBrindesScreen(self.frame, user_manager),
            'movimentacoes': lambda: MovimentacoesScreen(self.frame),
            'relatorios': lambda: RelatoriosScreen(self.frame),
            'configuracoes': lambda: ConfiguracoesScreen(self.frame),
        }
    
    def show_screen(self, screen_name):
        """Mostra uma tela específica"""
        # Ocultar tela atual
        if self.current_screen:
            self.current_screen.hide()
        
        # Garantir instância da tela (lazy init)
        if screen_name not in self.screens:
            factory = self.screen_factories.get(screen_name)
            if factory:
                try:
                    self.screens[screen_name] = factory()
                except Exception as e:
                    # Falha ao criar tela: registrar e abortar
                    import traceback
                    print(f"Erro ao inicializar tela '{screen_name}': {e}")
                    traceback.print_exc()
                    return

        # Mostrar nova tela
        if screen_name in self.screens:
            self.screens[screen_name].show()
            self.current_screen = self.screens[screen_name]
    
    def show_dashboard(self):
        """Mostra a tela de dashboard"""
        self.show_screen('dashboard')
    
    def show_brindes(self):
        """Mostra a tela de brindes"""
        self.show_screen('brindes')

    def show_estoque_brindes(self):
        """Mostra a tela de estoque de brindes"""
        self.show_screen('estoque_brindes')
    
    def show_movimentacoes(self):
        """Mostra a tela de movimentações"""
        self.show_screen('movimentacoes')
    
    def show_relatorios(self):
        """Mostra a tela de relatórios"""
        self.show_screen('relatorios')
    
    def show_configuracoes(self):
        """Mostra a tela de configurações"""
        self.show_screen('configuracoes')
