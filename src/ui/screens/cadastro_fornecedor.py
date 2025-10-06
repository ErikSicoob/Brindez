"""
Tela de Cadastro/Edição de Fornecedor usando BaseFormScreen
"""

import customtkinter as ctk
from ..components.base_form_screen import BaseFormScreen
from ...data.data_provider import data_provider
from ...utils.validators import Validators, ValidationError

class CadastroFornecedorScreen(BaseFormScreen):
    """Tela de cadastro/edição de fornecedor otimizada"""
    
    def __init__(self, parent, user_manager, fornecedor_data=None, on_success=None):
        """Inicializa a tela de cadastro de fornecedor"""
        self.fornecedor_data = fornecedor_data
        self.is_edit_mode = fornecedor_data is not None
        
        title = "✏️ Editar Fornecedor" if self.is_edit_mode else "➕ Novo Fornecedor"
        subtitle = "Atualize os dados do fornecedor" if self.is_edit_mode else "Preencha os dados do fornecedor"
        
        super().__init__(parent, user_manager, title, subtitle, on_success)

    def setup_base_ui(self):
        """Configura a interface base do formulário com um frame rolável."""
        super().setup_base_ui()

        # Cria o frame rolável que servirá como o form_frame
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # O resto da configuração continua normalmente
        self.create_form_fields()
        self.load_defaults()
        self.create_buttons()
        
    def create_form_fields(self):
        """Cria os campos do formulário"""
        row = 0
        
        # Informações Básicas
        self.create_section_title("📋 Informações Básicas", row)
        row += 1
        
        # Nome da Empresa
        self.create_field_entry(
            "Nome da Empresa", "nome", row,
            placeholder="Ex: Brindes & Cia Ltda", required=True
        )
        row += 1
        
        # Nome do Contato
        self.create_field_entry(
            "Nome do Contato", "contato_nome", row,
            placeholder="Ex: João Silva"
        )
        row += 1
        
        # Informações de Contato
        self.create_section_title("📞 Informações de Contato", row)
        row += 1
        
        # Telefone
        self.create_field_entry(
            "Telefone", "telefone", row,
            placeholder="Ex: (11) 3333-4444"
        )
        row += 1
        
        # E-mail
        self.create_field_entry(
            "E-mail", "email", row,
            placeholder="Ex: contato@empresa.com.br"
        )
        row += 1
        
        # Endereço
        self.create_section_title("📍 Endereço", row)
        row += 1
        
        # Endereço
        self.create_field_entry(
            "Endereço", "endereco", row,
            placeholder="Ex: Rua das Flores, 123"
        )
        row += 1
        
        # Cidade
        self.create_field_entry(
            "Cidade", "cidade", row,
            placeholder="Ex: São Paulo"
        )
        row += 1
        
        # Estado
        self.create_field_entry(
            "Estado", "estado", row,
            placeholder="Ex: SP", width=100
        )
        row += 1
        
        # CEP
        self.create_field_entry(
            "CEP", "cep", row,
            placeholder="Ex: 01234-567", width=150
        )
        row += 1
        
        # Informações Fiscais
        self.create_section_title("🏢 Informações Fiscais", row)
        row += 1
        
        # CNPJ
        self.create_field_entry(
            "CNPJ", "cnpj", row,
            placeholder="Ex: 12.345.678/0001-90"
        )
        row += 1
        
        # Observações
        self.create_section_title("📝 Observações", row)
        row += 1
        
        # Observações
        self.create_field_textarea(
            "Observações", "observacoes", row,
            placeholder="Informações adicionais sobre o fornecedor...",
            height=80
        )
    
    def load_defaults(self):
        """Carrega valores padrão ou dados para edição"""
        if self.is_edit_mode and self.fornecedor_data:
            # Preencher campos com dados existentes
            for key, value in self.fornecedor_data.items():
                if key in self.field_widgets and value:
                    self.set_field_value(key, value)
    
    def validate_form(self):
        """Valida o formulário"""
        errors = self.validate_required_fields()
        data = self.get_form_data()
        
        # Validar e-mail se fornecido
        email = data.get('email', '').strip()
        if email:
            try:
                Validators.validate_email(email, 'E-mail')
            except ValidationError as e:
                errors.append(str(e))
        
        return errors
    
    def process_save(self, data):
        """Processa o salvamento dos dados"""
        try:
            # Adicionar usuário atual se for novo cadastro
            if not self.is_edit_mode:
                user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
                if user:
                    data['usuario_criacao_id'] = user.get('id', 1)
            
            # Salvar ou atualizar
            if self.is_edit_mode:
                success = data_provider.update_fornecedor(self.fornecedor_data['id'], data)
            else:
                success = data_provider.create_fornecedor(data)
            
            return success
            
        except Exception as e:
            print(f"Erro ao salvar fornecedor: {e}")
            return False
