"""
Componente do menu lateral da aplicação
"""

import customtkinter as ctk

class Sidebar:
    """Classe do menu lateral"""
    
    def __init__(self, parent, on_menu_select_callback):
        """Inicializa o menu lateral"""
        self.parent = parent
        self.on_menu_select = on_menu_select_callback
        self.selected_button = None
        
        # Criar frame principal
        self.frame = ctk.CTkFrame(parent, width=200)
        self.frame.grid_propagate(False)  # Manter largura fixa
        
        # Definir itens do menu
        self.menu_items = [
            {'key': 'dashboard', 'text': '📊 Dashboard', 'icon': '📊'},
            {'key': 'brindes', 'text': '🎁 Brindes', 'icon': '🎁'},
            {'key': 'estoque_brindes', 'text': '📦 Estoque de Brindes', 'icon': '📦'},
            {'key': 'movimentacoes', 'text': '📦 Movimentações', 'icon': '📦'},
            {'key': 'fornecedores', 'text': '🏢 Fornecedores', 'icon': '🏢'},
            {'key': 'relatorios', 'text': '📈 Relatórios', 'icon': '📈'},
            {'key': 'configuracoes', 'text': '⚙️ Configurações', 'icon': '⚙️'}
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do menu lateral"""
        # Título do menu
        self.menu_title = ctk.CTkLabel(
            self.frame,
            text="MENU PRINCIPAL",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.menu_title.pack(pady=(20, 10), padx=20)
        
        # Separador
        separator = ctk.CTkFrame(self.frame, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill="x", padx=20, pady=(0, 20))
        
        # Criar botões do menu
        self.menu_buttons = {}
        for item in self.menu_items:
            button = ctk.CTkButton(
                self.frame,
                text=item['text'],
                command=lambda key=item['key']: self.select_menu_item(key),
                anchor="w",
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color=("#00AE9D", "#00AE9D"),
                hover_color=("#008f82", "#008f82")
            )
            button.pack(fill="x", padx=15, pady=5)
            self.menu_buttons[item['key']] = button
        
        # Selecionar dashboard por padrão
        self.select_menu_item('dashboard')
        
        # Espaço flexível
        spacer = ctk.CTkFrame(self.frame, fg_color="transparent")
        spacer.pack(fill="both", expand=True, pady=20)
        
        # Informações da versão (no rodapé)
        self.version_label = ctk.CTkLabel(
            self.frame,
            text="v1.0.0 - Beta",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        self.version_label.pack(side="bottom", pady=(0, 20))
    
    def select_menu_item(self, menu_key):
        """Seleciona um item do menu"""
        # Resetar cor do botão anterior para cor padrão (não clicado)
        if self.selected_button:
            self.selected_button.configure(fg_color=("#00AE9D", "#00AE9D"))
        
        # Destacar botão atual
        current_button = self.menu_buttons[menu_key]
        current_button.configure(fg_color=("#003641", "#003641"))
        self.selected_button = current_button
        
        # Chamar callback
        if self.on_menu_select:
            self.on_menu_select(menu_key)
