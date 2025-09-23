import customtkinter as ctk

class FormInline:
    """Formulário inline que aparece dentro da janela principal"""
    
    def __init__(self, parent, title: str, fields: list, on_submit: callable, submit_text: str = "Salvar", on_cancel: callable = None):
        """
        Inicializa o formulário inline
        
        Args:
            parent: Widget pai onde o formulário será exibido
            title: Título do formulário
            fields: Lista de campos do formulário
            on_submit: Função callback para quando o formulário for submetido
            submit_text: Texto do botão de submit
            on_cancel: Função callback para quando o formulário for cancelado
        """
        self.parent = parent
        self.title = title
        self.fields = fields
        self.on_submit = on_submit
        self.submit_text = submit_text
        self.on_cancel = on_cancel
        self.form_frame = None
        self.form_data = {}
        self.validation_errors = {}
        
    def show(self):
        """Exibe o formulário inline"""
        # Se já existe um formulário, removê-lo
        if self.form_frame and self.form_frame.winfo_exists():
            self.form_frame.destroy()
        
        # Criar frame principal do formulário
        self.form_frame = ctk.CTkFrame(self.parent, fg_color=("gray95", "gray16"))
        self.form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            self.form_frame,
            text=self.title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame para os campos
        fields_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=20, pady=10)
        fields_frame.columnconfigure(1, weight=1)
        
        # Criar campos
        self.form_data = {}
        self.validation_errors = {}
        row = 0
        
        for field in self.fields:
            # Label
            label = ctk.CTkLabel(
                fields_frame,
                text=field.get('label', ''),
                font=ctk.CTkFont(weight="bold")
            )
            label.grid(row=row, column=0, padx=(0, 10), pady=10, sticky="w")
            
            # Campo de entrada
            field_type = field.get('type', 'entry')
            field_key = field.get('key')
            
            if field_type == 'entry':
                widget = ctk.CTkEntry(
                    fields_frame,
                    placeholder_text=field.get('placeholder', ''),
                    show="*" if field.get('type') == 'password' else ""
                )
            elif field_type == 'combo':
                widget = ctk.CTkComboBox(
                    fields_frame,
                    values=field.get('options', []),
                    state="readonly"
                )
                # Definir valor padrão se existir
                if 'default' in field:
                    widget.set(field['default'])
            elif field_type == 'checkbox':
                widget = ctk.CTkCheckBox(fields_frame, text="")
                if field.get('default', False):
                    widget.select()
            elif field_type == 'textarea':
                widget = ctk.CTkTextbox(fields_frame, height=100)
            else:
                widget = ctk.CTkEntry(fields_frame)
            
            # Definir valor padrão
            if 'default' in field and field_type != 'combo':
                if field_type == 'checkbox':
                    if field['default']:
                        widget.select()
                else:
                    widget.insert(0, str(field['default']))
            
            widget.grid(row=row, column=1, padx=(0, 10), pady=10, sticky="ew")
            
            # Armazenar referência e dados
            self.form_data[field_key] = widget
            
            # Mensagem de erro
            error_label = ctk.CTkLabel(
                fields_frame,
                text="",
                text_color="red",
                font=ctk.CTkFont(size=10)
            )
            error_label.grid(row=row, column=2, padx=(10, 0), pady=10, sticky="w")
            self.validation_errors[field_key] = error_label
            
            row += 1
        
        # Botões
        buttons_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            fg_color="red",
            hover_color="darkred",
            command=self.on_cancel if self.on_cancel else self.hide
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        submit_btn = ctk.CTkButton(
            buttons_frame,
            text=self.submit_text,
            command=self._validate_and_submit
        )
        submit_btn.pack(side="left")
    
    def hide(self):
        """Oculta o formulário inline"""
        if self.form_frame and self.form_frame.winfo_exists():
            self.form_frame.destroy()
    
    def _validate_and_submit(self):
        """Valida os dados e submete o formulário"""
        # Limpar erros anteriores
        for error_label in self.validation_errors.values():
            error_label.configure(text="")
        
        form_data = {}
        has_errors = False
        
        # Coletar dados
        for field in self.fields:
            field_key = field.get('key')
            field_type = field.get('type', 'entry')
            widget = self.form_data[field_key]
            
            if field_type == 'checkbox':
                value = widget.get() == 1
            elif field_type == 'combo':
                value = widget.get()
            elif field_type == 'textarea':
                value = widget.get("0.0", "end").strip()
            else:
                value = widget.get().strip()
            
            # Validação obrigatória
            if field.get('required', False) and not value:
                self.validation_errors[field_key].configure(text="Campo obrigatório")
                has_errors = True
                continue
            
            # Validação de e-mail
            if field.get('validation') == 'email' and value:
                import re
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    self.validation_errors[field_key].configure(text="E-mail inválido")
                    has_errors = True
                    continue
            
            form_data[field_key] = value
        
        if not has_errors:
            # Chamar callback de submit
            if self.on_submit:
                self.on_submit(form_data)
    
    def set_field_value(self, field_key: str, value: str):
        """Define o valor de um campo específico"""
        if field_key in self.form_data:
            widget = self.form_data[field_key]
            if hasattr(widget, 'delete'):
                widget.delete(0, "end")
                widget.insert(0, str(value))
            elif hasattr(widget, 'set'):
                widget.set(str(value))
