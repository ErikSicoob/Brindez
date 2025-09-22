"""
Componente da área de conteúdo principal
"""

import customtkinter as ctk
from ..screens.dashboard import DashboardScreen
from ..screens.brindes import BrindesScreen
from ..screens.movimentacoes import MovimentacoesScreen
from ..screens.relatorios import RelatoriosScreen
from ..screens.configuracoes import ConfiguracoesScreen

class ContentArea:
    """Classe da área de conteúdo principal"""
    
    def __init__(self, parent):
        """Inicializa a área de conteúdo"""
        self.parent = parent
        self.current_screen = None
        
        # Criar frame principal
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        
        # Inicializar telas
        self.screens = {}
        self.setup_screens()
    
    def setup_screens(self):
        """Configura todas as telas da aplicação"""
        # Criar instâncias das telas (inicialmente ocultas)
        self.screens['dashboard'] = DashboardScreen(self.frame)
        self.screens['brindes'] = BrindesScreen(self.frame)
        self.screens['movimentacoes'] = MovimentacoesScreen(self.frame)
        self.screens['relatorios'] = RelatoriosScreen(self.frame)
        self.screens['configuracoes'] = ConfiguracoesScreen(self.frame)
    
    def show_screen(self, screen_name):
        """Mostra uma tela específica"""
        # Ocultar tela atual
        if self.current_screen:
            self.current_screen.hide()
        
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
    
    def show_movimentacoes(self):
        """Mostra a tela de movimentações"""
        self.show_screen('movimentacoes')
    
    def show_relatorios(self):
        """Mostra a tela de relatórios"""
        self.show_screen('relatorios')
    
    def show_configuracoes(self):
        """Mostra a tela de configurações"""
        self.show_screen('configuracoes')
