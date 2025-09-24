"""
Janela principal da aplicação
"""

import customtkinter as ctk
import tkinter as tk
from .components.sidebar import Sidebar
from .components.content_area import ContentArea
from .components.header import Header

class MainWindow:
    """Classe da janela principal"""
    
    def __init__(self, root, current_user):
        """Inicializa a janela principal"""
        self.root = root
        self.current_user = current_user
        
        # Configurar grid da janela principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Criar componentes principais
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface principal"""
        # Header (barra superior)
        self.header = Header(self.root, self.current_user)
        self.header.frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        # Content Area (área de conteúdo) - criar primeiro
        self.content_area = ContentArea(self.root, self.current_user)
        self.content_area.frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        
        # Sidebar (menu lateral) - criar depois do content_area
        self.sidebar = Sidebar(self.root, self.on_menu_select)
        self.sidebar.frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        # Mostrar dashboard inicial
        self.content_area.show_dashboard()
    
    def on_menu_select(self, menu_item):
        """Callback para seleção de menu"""
        print(f"Menu selecionado: {menu_item}")
        
        # Mapear itens do menu para telas
        menu_mapping = {
            'dashboard': self.content_area.show_dashboard,
            'brindes': self.content_area.show_brindes,
            'estoque_brindes': self.content_area.show_estoque_brindes,
            'movimentacoes': self.content_area.show_movimentacoes,
            'relatorios': self.content_area.show_relatorios,
            'configuracoes': self.content_area.show_configuracoes
        }
        
        # Executar função correspondente
        if menu_item in menu_mapping:
            menu_mapping[menu_item]()
