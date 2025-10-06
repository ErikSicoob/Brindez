"""
Script para corrigir problemas de layout no sistema de cadastro de brindes.
"""

def fix_base_form_screen():
    """Corrige o layout do BaseFormScreen para usar grid corretamente."""
    content = """"""
    """Classe base para telas de formulário otimizadas"""
    
    def __init__(self, parent, user_manager, title, subtitle="", on_success=None, on_cancel=None):
        """Inicializa a tela de formulário base"""
        super().__init__(parent, user_manager, title)
        self.subtitle = subtitle
        self.on_success = on_success
        self.on_cancel = on_cancel
        self.field_widgets = {}
        self.custom_widgets = {}
        self.setup_base_ui()
        
    def setup_base_ui(self):
        """Configura a interface base do formulário"""
        try:
            # Configurar o frame principal para expandir
            self.frame.grid_rowconfigure(1, weight=1)
            self.frame.grid_columnconfigure(0, weight=1)
            
            # Título
            self.create_title(self.title, self.subtitle)
            
            # Frame principal do formulário - ocupar todo o espaço disponível
            self.form_frame = ctk.CTkScrollableFrame(self.frame)
            self.form_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
            self.form_frame.grid_columnconfigure(0, weight=1)
            
            # Criar campos do formulário (implementado pelas subclasses)
            self.create_form_fields()
            
            # Frame dos botões - fixo no rodapé
            self.create_buttons()
            
            # Carregar valores padrão (implementado pelas subclasses)
            self.load_defaults()
            
        except Exception as e:
            print(f"Erro ao configurar interface do formulário: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def create_field_entry(self, label, key, row, placeholder="", required=False, field_type="text", width=None):
        """Cria um campo de entrada"""
        # Container do campo
        field_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="ew", pady=8, padx=10)
        field_container.grid_columnconfigure(0, weight=1)
        
        # Label
        label_text = label
        if required:
            label_text += " *"
            
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry
        entry_kwargs = {
            'placeholder_text': placeholder,
            'height': 35,
            'font': ctk.CTkFont(size=11)
        }
        
        # Adicionar width apenas se fornecido
        if width is not None:
            entry_kwargs['width'] = width
            
        entry = ctk.CTkEntry(field_container, **entry_kwargs)
        entry.grid(row=1, column=0, sticky="ew")
        
        # Armazenar referência
        self.field_widgets[key] = {
            'widget': entry,
            'type': field_type,
            'required': required,
            'label': label
        }
        
        return entry
    
    def create_field_combobox(self, label, key, row, options=None, required=False, width=None):
        """Cria um campo combobox"""
        if options is None:
            options = []
            
        # Container do campo
        field_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="ew", pady=8, padx=10)
        field_container.grid_columnconfigure(0, weight=1)
        
        # Label
        label_text = label
        if required:
            label_text += " *"
            
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Combobox
        combo_kwargs = {
            'values': options,
            'height': 35,
            'font': ctk.CTkFont(size=11),
            'state': "readonly"
        }
        
        # Adicionar width apenas se fornecido
        if width is not None:
            combo_kwargs['width'] = width
            
        combobox = ctk.CTkComboBox(field_container, **combo_kwargs)
        combobox.grid(row=1, column=0, sticky="ew")
        
        # Definir valor padrão se houver opções
        if options:
            combobox.set("")  # Deixar vazio inicialmente
        
        # Armazenar referência
        self.field_widgets[key] = {
            'widget': combobox,
            'type': 'combobox',
            'required': required,
            'options': options,
            'label': label
        }
        
        return combobox
    
    def create_field_textarea(self, label, key, row, placeholder="", required=False, height=100):
        """Cria um campo de texto multilinha"""
        # Container do campo
        field_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="nsew", pady=8, padx=10)
        field_container.grid_columnconfigure(0, weight=1)
        field_container.grid_rowconfigure(1, weight=1)
        
        # Label
        label_text = label
        if required:
            label_text += " *"
            
        label_widget = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Textarea
        textarea = ctk.CTkTextbox(
            field_container,
            height=height,
            font=ctk.CTkFont(size=11)
        )
        textarea.grid(row=1, column=0, sticky="nsew")
        
        # Placeholder (simulado)
        if placeholder:
            textarea.insert("1.0", placeholder)
            textarea.configure(text_color=("gray50", "gray50"))
            
            def on_focus_in(event):
                if textarea.get("1.0", "end-1c") == placeholder:
                    textarea.delete("1.0", "end")
                    textarea.configure(text_color=("black", "white"))
            
            def on_focus_out(event):
                if not textarea.get("1.0", "end-1c").strip():
                    textarea.insert("1.0", placeholder)
                    textarea.configure(text_color=("gray50", "gray50"))
            
            textarea.bind("<FocusIn>", on_focus_in)
            textarea.bind("<FocusOut>", on_focus_out)
        
        # Armazenar referência
        self.field_widgets[key] = {
            'widget': textarea,
            'type': 'textarea',
            'required': required,
            'placeholder': placeholder,
            'label': label
        }
        
        return textarea
    
    def create_section_title(self, title, row, subtitle=""):
        """Cria um título de seção"""
        # Container da seção
        section_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        section_container.grid(row=row, column=0, sticky="ew", pady=(20, 10), padx=10)
        section_container.grid_columnconfigure(0, weight=1)
        
        # Título principal
        title_label = ctk.CTkLabel(
            section_container,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Subtítulo se fornecido
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                section_container,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray50"),
                anchor="w",
                wraplength=600
            )
            subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))
        
        return section_container
    
    def create_buttons(self):
        """Cria os botões do formulário"""
        buttons_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Botão Cancelar
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            command=self.cancel,
            fg_color=("#cc3333", "#cc3333"),
            hover_color=("#a82828", "#a82828"),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        # Botão Salvar
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self.save,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82"),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        save_btn.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
    
    def get_form_data(self):
        """Obtém os dados do formulário"""
        data = {}
        
        # Campos simples
        for key, field_info in self.field_widgets.items():
            widget = field_info['widget']
            field_type = field_info['type']
            
            if field_type == 'combobox':
                data[key] = widget.get()
            elif field_type == 'textarea':
                value = widget.get("1.0", "end-1c")
                placeholder = field_info.get('placeholder', '')
                if value == placeholder:
                    data[key] = ""
                else:
                    data[key] = value
            else:
                data[key] = widget.get().strip()
        
        return data
    
    def validate_required_fields(self):
        """Valida campos obrigatórios"""
        errors = []
        data = self.get_form_data()
        
        for key, field_info in self.field_widgets.items():
            if field_info['required']:
                value = data.get(key, '').strip()
                if not value:
                    field_name = field_info.get('label', key.replace('_', ' ').title())
                    errors.append(f"O campo '{field_name}' é obrigatório")
        
        return errors
    
    def validate_form(self):
        """Valida o formulário - pode ser sobrescrito pelas subclasses"""
        return self.validate_required_fields()
    
    def save(self):
        """Salva os dados - deve ser implementado pelas subclasses"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Erro de Validação", "\n".join(errors))
            return False
        
        try:
            data = self.get_form_data()
            success = self.process_save(data)
            
            if success and self.on_success:
                self.on_success()
            
            return success
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar: {str(e)}")
            return False
    
    def process_save(self, data):
        """Processa o salvamento dos dados - deve ser implementado pelas subclasses"""
        raise NotImplementedError("Método process_save deve ser implementado pelas subclasses")
    
    def cancel(self):
        """Cancela o formulário"""
        if self.has_data():
            if not messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar? Todas as alterações serão perdidas."):
                return
        
        if self.on_cancel:
            self.on_cancel()
        else:
            self.destroy()
    
    def has_data(self):
        """Verifica se há dados no formulário"""
        data = self.get_form_data()
        return any(data.values())
    
    def clear_form(self):
        """Limpa o formulário"""
        for field_info in self.field_widgets.values():
            widget = field_info['widget']
            if field_info['type'] == 'combobox':
                widget.set("")
            elif field_info['type'] == 'textarea':
                widget.delete("1.0", "end")
                if 'placeholder' in field_info:
                    widget.insert("1.0", field_info['placeholder'])
                    widget.configure(text_color=("gray50", "gray50"))
            else:
                widget.delete(0, "end")
    
    def set_field_value(self, key, value):
        """Define o valor de um campo"""
        if key not in self.field_widgets:
            return
            
        field_info = self.field_widgets[key]
        widget = field_info['widget']
        
        if field_info['type'] == 'combobox':
            widget.set(value)
        elif field_info['type'] == 'textarea':
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
            widget.configure(text_color=("black", "white"))
        else:
            widget.delete(0, "end")
            widget.insert(0, str(value))
    
    def get_field_value(self, key):
        """Obtém o valor de um campo"""
        if key not in self.field_widgets:
            return None
            
        field_info = self.field_widgets[key]
        widget = field_info['widget']
        
        if field_info['type'] == 'combobox':
            return widget.get()
        elif field_info['type'] == 'textarea':
            return widget.get("1.0", "end-1c")
        else:
            return widget.get()
"""
    with open("c:\\Pojetos - DEV\\Brindez\\src\\ui\\components\\base_form_screen.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_base_form_screen()
    print("Correções aplicadas com sucesso!")
