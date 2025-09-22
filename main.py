"""
Sistema de Controle de Brindes
Aplicação principal para gestão de estoque de brindes
"""

import customtkinter as ctk
import sys
import os
from src.app import BrindeApp

def main():
    """Função principal da aplicação"""
    try:
        # Configurações iniciais do CustomTkinter
        ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Criar e executar a aplicação
        app = BrindeApp()
        app.run()
        
    except Exception as e:
        print(f"Erro ao inicializar a aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
