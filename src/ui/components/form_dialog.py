"""
Componente de diálogo para formulários inline
"""

import customtkinter as ctk
from tkinter import messagebox
from ...utils.validators import Validators, ValidationError

class FormDialog:
    """Classe para criar diálogos de formulário inline"""
    
    def __init__(self, parent, title, fields, on_submit=None, on_cancel=None, show_header: bool = True):
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
        self.show_header = show_header
        
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
        # Definir tamanho inicial proporcional à tela e permitir redimensionamento
        try:
            sw = self.dialog.winfo_screenwidth()
            sh = self.dialog.winfo_screenheight()
            w = min(600, int(sw * 0.45))
            h = min(650, int(sh * 0.65))
            self.dialog.geometry(f"{w}x{h}")
        except Exception:
            self.dialog.geometry("520x560")
        self.dialog.resizable(True, True)
        # Garantir tamanho mínimo para não cortar a área dos botões
        try:
            self.dialog.minsize(520, 520)
        except Exception:
            pass
        
        # Centralizar na tela
        self.dialog.after(100, self.center_dialog)  # Atrasar a centralização
        
        # Configurar como modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        try:
            self.dialog.lift()
            self.dialog.focus_force()
        except Exception:
            pass
        
        # Configurar grid
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_rowconfigure(0, weight=0)  # Header
        self.dialog.grid_rowconfigure(1, weight=1)  # Form
        self.dialog.grid_rowconfigure(2, weight=0)  # Buttons

        # Criar interface
        if self.show_header:
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
        title_label.pack(pady=8)
    
    def create_form(self, data=None):
        """Cria o formulário com estrutura simplificada"""
        # Frame scrollável simples para o formulário
        # Altura levemente reduzida para garantir espaço fixo aos botões no rodapé
        self.form_frame = ctk.CTkScrollableFrame(self.dialog, height=300)
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.form_frame.grid_columnconfigure(0, weight=1)
        
        # Criar campos diretamente no form_frame
        for i, field in enumerate(self.fields):
            self.create_field(self.form_frame, field, i, data)

        # Linha de botões inline (garantia de visibilidade em telas pequenas)
        try:
            inline_buttons = ctk.CTkFrame(self.form_frame, fg_color="transparent")
            inline_buttons.grid(row=len(self.fields) + 1, column=0, sticky="ew", pady=(10, 10))
            inline_buttons.grid_columnconfigure((0, 1), weight=1)

            cancel_btn2 = ctk.CTkButton(
                inline_buttons,
                text="❌ Cancelar",
                command=self.cancel,
                fg_color=("#cc3333", "#cc3333"),
                hover_color=("#a82828", "#a82828"),
                height=36
            )
            cancel_btn2.grid(row=0, column=0, padx=(0, 5), sticky="ew")

            save_btn2 = ctk.CTkButton(
                inline_buttons,
                text="💾 Salvar",
                command=self.submit,
                fg_color=("#00AE9D", "#00AE9D"),
                hover_color=("#008f82", "#008f82"),
                height=36
            )
            save_btn2.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        except Exception:
            pass

    def create_field(self, parent, field, row, data=None):
        """Cria um campo do formulário com estrutura simplificada"""
        # Container para o campo
        field_container = ctk.CTkFrame(parent, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        field_container.grid_columnconfigure(0, weight=1)
        
        # Label do campo
        label_text = field['label']
        if field.get('required', False):
            label_text += " *"
            
        label = ctk.CTkLabel(
            field_container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Widget do campo baseado no tipo
        field_type = field.get('type', 'entry')
        field_key = field['key']
        widget = None
        
        if field_type == 'entry':
            widget = ctk.CTkEntry(
                field_container,
                placeholder_text=field.get('placeholder', ''),
                height=35
            )
            
        elif field_type == 'textarea':
            widget = ctk.CTkTextbox(
                field_container,
                height=80
            )
            
        elif field_type == 'combobox':
            widget = ctk.CTkComboBox(
                field_container,
                values=field.get('options', []),
                height=35
            )
            
        elif field_type == 'number':
            widget = ctk.CTkEntry(
                field_container,
                placeholder_text=field.get('placeholder', '0'),
                height=35
            )
            
        elif field_type == 'checkbox_group':
            # Para checkbox_group, criar um frame simples
            widget_frame = ctk.CTkFrame(field_container, fg_color="transparent")
            widget_frame.grid(row=1, column=0, sticky="ew", pady=2)
            
            checkboxes = {}
            options = field.get('options', [])
            
            for i, option in enumerate(options):
                var = ctk.IntVar()
                cb = ctk.CTkCheckBox(widget_frame, text=str(option), variable=var)
                cb.grid(row=i, column=0, padx=5, pady=2, sticky="w")
                checkboxes[str(option)] = var
            
            widget = checkboxes
            # Para checkbox_group, não chamamos grid() porque já foi posicionado
        
        elif field_type == 'checkbox_group_quantities':
            # Checkboxes com entrada de quantidade por opção
            widget_frame = ctk.CTkFrame(field_container, fg_color="transparent")
            widget_frame.grid(row=1, column=0, sticky="ew", pady=2)
            widget_frame.grid_columnconfigure((0, 1), weight=1)

            option_widgets = {}
            options = field.get('options', [])

            for i, option in enumerate(options):
                var = ctk.IntVar()
                cb = ctk.CTkCheckBox(widget_frame, text=str(option), variable=var)
                cb.grid(row=i, column=0, padx=5, pady=2, sticky="w")

                qty_entry = ctk.CTkEntry(widget_frame, placeholder_text="0", width=80)
                qty_entry.grid(row=i, column=1, padx=5, pady=2, sticky="e")
                qty_entry.configure(state="disabled")

                def make_toggle(entry_ref, var_ref):
                    def _toggle():
                        if var_ref.get() == 1:
                            entry_ref.configure(state="normal")
                            # Preencher com 0 se vazio
                            try:
                                if not entry_ref.get():
                                    entry_ref.insert(0, "0")
                            except Exception:
                                pass
                        else:
                            entry_ref.delete(0, "end")
                            entry_ref.insert(0, "0")
                            entry_ref.configure(state="disabled")
                    return _toggle

                cb.configure(command=make_toggle(qty_entry, var))

                option_widgets[str(option)] = (var, qty_entry)

            widget = option_widgets
            
        elif field_type == 'checkbox':
            widget = ctk.CTkCheckBox(field_container, text="")
            
        elif field_type == 'label':
            widget = ctk.CTkLabel(field_container, text="", anchor="w", justify="left")
            
        else:  # entry padrão
            widget = ctk.CTkEntry(
                field_container,
                placeholder_text=field.get('placeholder', ''),
                height=35
            )
        
        # Posicionar o widget (exceto checkbox_group que já foi posicionado)
        if field_type != 'checkbox_group' and widget is not None:
            widget.grid(row=1, column=0, sticky="ew", pady=2)
        
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
        elif field_type == 'checkbox_group':
            for key, var in widget.items():
                var.set(1 if key in value else 0)
        elif field_type == 'checkbox_group_quantities':
            # Espera dict {option: quantidade}
            for key, (var, entry) in widget.items():
                if isinstance(value, dict) and key in value and value[key] is not None:
                    var.set(1)
                    entry.configure(state="normal")
                    entry.delete(0, "end")
                    entry.insert(0, str(value[key]))
                else:
                    var.set(0)
                    entry.delete(0, "end")
                    entry.insert(0, "0")
                    entry.configure(state="disabled")
        elif field_type == 'checkbox':
            widget.select() if value else widget.deselect()
        elif field_type == 'label':
            widget.configure(text=str(value))
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
        elif field_type == 'checkbox_group':
            return [key for key, var in widget.items() if var.get() == 1]
        elif field_type == 'checkbox_group_quantities':
            # Retornar apenas as opções marcadas com suas quantidades (int)
            result = {}
            for key, (var, entry) in widget.items():
                if var.get() == 1:
                    txt = (entry.get() or '').strip()
                    try:
                        qty = int(txt)
                    except Exception:
                        qty = 0
                    result[key] = qty
            return result
        elif field_type == 'checkbox':
            return widget.get() == 1
        elif field_type == 'label':
            return None # Labels não têm valor
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
            fg_color=("#cc3333", "#cc3333"),
            hover_color=("#a82828", "#a82828"),
            height=40
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="ew")
        
        # Botão Salvar
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Salvar",
            command=self.submit,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82"),
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
