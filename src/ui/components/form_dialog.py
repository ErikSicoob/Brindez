"""
Componente de diálogo para formulários inline
"""

import customtkinter as ctk
from tkinter import messagebox
from ...utils.validators import Validators, ValidationError

class FormDialog:
    """Classe para criar diálogos de formulário inline"""
    
    def __init__(self, parent, title, fields, on_submit=None, on_cancel=None):
        """
        Inicializa o diálogo de formulário
        
        Args:
            parent: Widget pai
            title: Título do formulário
            fields: Lista de dicionários com configuração dos campos
            on_submit: Callback para submissão
            on_cancel: Callback para cancelamento
        """
        self.parent = parent
        self.title = title
        self.fields = fields
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        
        self.dialog = None
        self.field_widgets = {}
        self.is_visible = False
        
    def show(self, data=None):
        """Mostra o diálogo"""
        if self.is_visible:
            return
            
        # Criar janela de diálogo
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        
        # Centralizar na tela
        self.center_dialog()
        
        # Configurar como modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Configurar grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(1, weight=1)
        
        # Criar interface
        self.create_header()
        self.create_form(data)
        self.create_buttons()
        
        # Configurar eventos
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.is_visible = True
        
    def center_dialog(self):
        """Centraliza o diálogo na tela"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_header(self):
        """Cria o cabeçalho do formulário"""
        header_frame = ctk.CTkFrame(self.dialog)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=15)
    
    def create_form(self, data=None):
        """Cria o formulário"""
        # Frame scrollável para o formulário
        form_frame = ctk.CTkScrollableFrame(self.dialog)
        form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Criar campos
        for i, field in enumerate(self.fields):
            self.create_field(form_frame, field, i, data)
    
    def create_field(self, parent, field, row, data=None):
        """Cria um campo do formulário"""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.grid(row=row, column=0, sticky="ew", pady=5)
        field_frame.grid_columnconfigure(0, weight=1)
        
        # Label do campo
        label_text = field['label']
        if field.get('required', False):
            label_text += " *"
            
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Widget do campo baseado no tipo
        field_type = field.get('type', 'entry')
        field_key = field['key']
        
        if field_type == 'entry':
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=field.get('placeholder', ''),
                height=35
            )
            
        elif field_type == 'textarea':
            widget = ctk.CTkTextbox(
                field_frame,
                height=80
            )
            
        elif field_type == 'combobox':
            widget = ctk.CTkComboBox(
                field_frame,
                values=field.get('options', []),
                height=35
            )
            
        elif field_type == 'number':
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=field.get('placeholder', '0'),
                height=35
            )
            
        else:  # entry padrão
            widget = ctk.CTkEntry(
                field_frame,
                placeholder_text=field.get('placeholder', ''),
                height=35
            )
        
        widget.grid(row=1, column=0, sticky="ew")
        
        # Armazenar referência do widget
        self.field_widgets[field_key] = {
            'widget': widget,
            'type': field_type,
            'required': field.get('required', False),
            'validation': field.get('validation', None)
        }
        
        # Preencher com dados se fornecidos
        if data and field_key in data:
            self.set_field_value(field_key, data[field_key])
    
    def set_field_value(self, field_key, value):
        """Define o valor de um campo"""
        if field_key not in self.field_widgets:
            return
            
        field_info = self.field_widgets[field_key]
        widget = field_info['widget']
        field_type = field_info['type']
        
        if field_type == 'textarea':
            widget.delete("1.0", "end")
            widget.insert("1.0", str(value))
        elif field_type == 'combobox':
            widget.set(str(value))
        else:  # entry, number
            widget.delete(0, "end")
            widget.insert(0, str(value))
    
    def get_field_value(self, field_key):
        """Obtém o valor de um campo"""
        if field_key not in self.field_widgets:
            return None
            
        field_info = self.field_widgets[field_key]
        widget = field_info['widget']
        field_type = field_info['type']
        
        if field_type == 'textarea':
            return widget.get("1.0", "end-1c").strip()
        elif field_type == 'combobox':
            return widget.get()
        else:  # entry, number
            return widget.get().strip()
    
    def create_buttons(self):
        """Cria os botões do formulário"""
        buttons_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            command=self.cancel,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
            height=40
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")
        
        # Botão Salvar
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self.submit,
            height=40
        )
        save_btn.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="ew")
    
    def validate_form(self):
        """Valida o formulário usando o sistema de validações"""
        errors = []
        
        for field_key, field_info in self.field_widgets.items():
            value = self.get_field_value(field_key)
            field_label = next(f['label'] for f in self.fields if f['key'] == field_key)
            
            try:
                # Verificar campos obrigatórios
                if field_info['required']:
                    Validators.validate_required(value, field_label)
                
                # Validações específicas
                validation = field_info.get('validation')
                if validation and value:
                    if validation == 'number':
                        Validators.validate_non_negative_number(value, field_label)
                    elif validation == 'positive_number':
                        Validators.validate_positive_number(value, field_label)
                    elif validation == 'positive_integer':
                        Validators.validate_positive_integer(value, field_label)
                    elif validation == 'email':
                        Validators.validate_email(value, field_label)
                
                # Validações de comprimento
                field_config = next(f for f in self.fields if f['key'] == field_key)
                min_length = field_config.get('min_length', 0)
                max_length = field_config.get('max_length')
                
                if value and isinstance(value, str) and (min_length > 0 or max_length):
                    Validators.validate_string_length(value, field_label, min_length, max_length)
                    
            except ValidationError as e:
                errors.append(str(e))
        
        return errors
    
    def get_form_data(self):
        """Obtém todos os dados do formulário"""
        data = {}
        for field_key in self.field_widgets.keys():
            data[field_key] = self.get_field_value(field_key)
        return data
    
    def submit(self):
        """Submete o formulário"""
        # Validar formulário
        errors = self.validate_form()
        if errors:
            error_message = "Erros encontrados:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Erro de Validação", error_message)
            return
        
        # Obter dados
        data = self.get_form_data()
        
        # Chamar callback
        if self.on_submit:
            try:
                result = self.on_submit(data)
                if result is not False:  # Se não retornou False, fechar diálogo
                    self.close()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        else:
            self.close()
    
    def cancel(self):
        """Cancela o formulário"""
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def close(self):
        """Fecha o diálogo"""
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None
        self.is_visible = False
