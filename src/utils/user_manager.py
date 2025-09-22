"""
Gerenciador de usuários e permissões
"""

import getpass
import os
from .audit_logger import audit_logger

class UserManager:
    """Classe para gerenciar usuários e permissões"""
    
    def __init__(self):
        """Inicializa o gerenciador de usuários"""
        self.current_user = None
        
        # Mock de usuários para desenvolvimento
        # TODO: Substituir por consulta ao banco de dados
        self.mock_users = {
            'admin': {
                'username': 'admin',
                'name': 'Administrador',
                'filial': 'Matriz',
                'profile': 'Admin',
                'active': True
            },
            'joao.silva': {
                'username': 'joao.silva',
                'name': 'João Silva',
                'filial': 'Filial SP',
                'profile': 'Gestor',
                'active': True
            },
            'maria.santos': {
                'username': 'maria.santos',
                'name': 'Maria Santos',
                'filial': 'Filial RJ',
                'profile': 'Usuario',
                'active': True
            }
        }
    
    def get_windows_user(self):
        """Obtém o usuário atual do Windows"""
        try:
            return getpass.getuser().lower()
        except Exception:
            return 'admin'  # Fallback para desenvolvimento
    
    def authenticate_user(self):
        """Autentica o usuário baseado no login do Windows"""
        windows_user = self.get_windows_user()
        
        # Verificar se o usuário existe no sistema
        if windows_user in self.mock_users:
            user_data = self.mock_users[windows_user]
            if user_data['active']:
                self.current_user = user_data
                audit_logger.audit_user_login(windows_user, True)
                return True, "Usuário autenticado com sucesso"
            else:
                audit_logger.audit_user_login(windows_user, False)
                return False, "Usuário inativo"
        else:
            # Para desenvolvimento, criar usuário temporário como Admin
            self.current_user = {
                'username': windows_user,
                'name': f'Usuário {windows_user.title()}',
                'filial': 'Matriz',
                'profile': 'Admin',
                'active': True
            }
            audit_logger.audit_user_login(windows_user, True)
            return True, "Usuário temporário criado (modo desenvolvimento)"
    
    def get_current_user(self):
        """Retorna o usuário atual"""
        return self.current_user
    
    def has_permission(self, permission):
        """Verifica se o usuário atual tem uma permissão específica"""
        if not self.current_user:
            return False
        
        profile = self.current_user.get('profile', 'Usuario')
        
        # Definir permissões por perfil
        permissions = {
            'Admin': [
                'view_all_filiais',
                'manage_users',
                'manage_filiais',
                'manage_categories',
                'manage_units',
                'generate_reports',
                'manage_stock',
                'transfer_items',
                'system_config'
            ],
            'Gestor': [
                'view_own_filial',
                'generate_reports',
                'manage_stock',
                'transfer_items'
            ],
            'Usuario': [
                'view_own_filial',
                'stock_exit'
            ]
        }
        
        user_permissions = permissions.get(profile, [])
        return permission in user_permissions
    
    def can_view_filial(self, filial):
        """Verifica se o usuário pode visualizar dados de uma filial"""
        if not self.current_user:
            return False
        
        # Admin pode ver todas as filiais
        if self.current_user.get('profile') == 'Admin':
            return True
        
        # Matriz pode ver todas as filiais
        if self.current_user.get('filial') == 'Matriz':
            return True
        
        # Outros usuários só podem ver sua própria filial
        return self.current_user.get('filial') == filial
    
    def get_accessible_filiais(self):
        """Retorna lista de filiais que o usuário pode acessar"""
        if not self.current_user:
            return []
        
        # Mock de filiais
        all_filiais = ['Matriz', 'Filial SP', 'Filial RJ', 'Filial BH']
        
        # Admin e Matriz podem ver todas
        if (self.current_user.get('profile') == 'Admin' or 
            self.current_user.get('filial') == 'Matriz'):
            return all_filiais
        
        # Outros usuários só veem sua filial
        return [self.current_user.get('filial')]
    
    def log_action(self, action, details=None):
        """Registra uma ação do usuário (para auditoria)"""
        # TODO: Implementar sistema de logs
        if self.current_user:
            print(f"LOG: {self.current_user['username']} - {action}")
            if details:
                print(f"     Detalhes: {details}")
    
    def is_admin(self):
        """Verifica se o usuário atual é admin"""
        return self.current_user and self.current_user.get('profile') == 'Admin'
    
    def is_gestor(self):
        """Verifica se o usuário atual é gestor"""
        return self.current_user and self.current_user.get('profile') == 'Gestor'
    
    def is_usuario(self):
        """Verifica se o usuário atual é usuário comum"""
        return self.current_user and self.current_user.get('profile') == 'Usuario'
