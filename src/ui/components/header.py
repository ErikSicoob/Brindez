"""
Componente do cabeçalho da aplicação
"""

import customtkinter as ctk
from datetime import datetime

class Header:
    """Classe do cabeçalho da aplicação"""
    
    def __init__(self, parent, current_user):
        """Inicializa o cabeçalho"""
        self.parent = parent
        self.current_user = current_user
        
        # Criar frame principal
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(1, weight=1)  # Coluna do meio expansível
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do cabeçalho"""
        # Logo/Título da aplicação
        self.title_label = ctk.CTkLabel(
            self.frame,
            text="🎁 Sistema de Controle de Brindes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Espaço flexível no meio
        spacer = ctk.CTkLabel(self.frame, text="")
        spacer.grid(row=0, column=1, sticky="ew")
        
        # Informações do usuário
        self.user_info_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.user_info_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Nome do usuário
        name = self.current_user.get('name', 'Usuário')
        self.user_label = ctk.CTkLabel(
            self.user_info_frame,
            text=f"👤 {name}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.user_label.grid(row=0, column=0, padx=(0, 10), sticky="e")
        
        # Filial
        filial = self.current_user.get('filial', 'N/A')
        self.filial_label = ctk.CTkLabel(
            self.user_info_frame,
            text=f"🏢 {filial}",
            font=ctk.CTkFont(size=11)
        )
        self.filial_label.grid(row=0, column=1, padx=(0, 10), sticky="e")
        
        # Perfil
        profile = self.current_user.get('profile', 'Usuario')
        profile_color = self.get_profile_color(profile)
        self.profile_label = ctk.CTkLabel(
            self.user_info_frame,
            text=f"🔑 {profile}",
            font=ctk.CTkFont(size=11),
            text_color=profile_color
        )
        self.profile_label.grid(row=0, column=2, sticky="e")
    
    def get_profile_color(self, profile):
        """Retorna cor baseada no perfil do usuário"""
        colors = {
            'Admin': '#e74c3c',      # Vermelho
            'Gestor': '#f39c12',     # Laranja
            'Usuario': '#27ae60'     # Verde
        }
        return colors.get(profile, '#7f8c8d')  # Cinza padrão
