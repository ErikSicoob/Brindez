"""
Script para corrigir problemas de layout na aplicação principal.
"""

def fix_app():
    """Corrige o layout da aplicação principal."""
    content = """"""
"""
Classe principal da aplicação Brinde
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import getpass
from .ui.main_window import MainWindow
from .utils.user_manager import UserManager

class BrindeApp:
    """Classe principal da aplicação"""
    
    def __init__(self):
        """Inicializa a aplicação"""
        self.root = None
        self.main_window = None
        self.user_manager = UserManager()
        self.current_user = None
        
    def initialize_user(self):
        """Inicializa o usuário atual baseado no login do Windows"""
        try:
            # Obtém o usuário atual do Windows
            windows_user = getpass.getuser()
            
            # Por enquanto, vamos simular um usuário admin para desenvolvimento
            # TODO: Implementar sistema real de usuários quando integrar com BD
            self.current_user = {
                'username': windows_user,
                'name': f'Usuário {windows_user}',
                'filial': 'Matriz',
                'profile': 'Admin'  # Admin, Gestor, Usuario
            }
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao identificar usuário: {e}")
            return False
    
    def run(self):
        """Executa a aplicação"""
        try:
            # Inicializar usuário
            if not self.initialize_user():
                return
            
            # Criar janela principal
            self.root = ctk.CTk()
            
            # Configurar janela
            self.root.title("Sistema de Controle de Brindes")
            self.root.minsize(1000, 600)
            
            # Configurar para iniciar maximizado
            self.root.after(0, self.maximize_window)
            
            # Criar a janela principal após a configuração
            self.main_window = MainWindow(self.root, self.current_user)
            
            # Iniciar loop principal
            self.root.mainloop()
            
        except Exception as e:
            messagebox.showerror("Erro Fatal", f"Erro ao executar aplicação: {e}")
    
    def maximize_window(self):
        """Maximiza a janela da aplicação"""
        # Tentar diferentes métodos para maximizar a janela
        try:
            # Método 1: state zoomed (Windows)
            self.root.state('zoomed')
        except:
            try:
                # Método 2: wm_state zoomed
                self.root.wm_state('zoomed')
            except:
                try:
                    # Método 3: geometry com tamanho da tela
                    self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
                except:
                    # Método 4: fallback para tamanho grande
                    self.root.geometry("1400x800+50+50")
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
"""
    with open("c:\\Pojetos - DEV\\Brindez\\src\\app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_app()
    print("Correções na aplicação principal aplicadas com sucesso!")
