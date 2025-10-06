"""
Tela de Cadastro de Brindes
"""

import customtkinter as ctk
from tkinter import messagebox
from ..components.base_form_screen import BaseFormScreen
from ...data.data_provider import data_provider
from ...utils.validators import BrindeValidator, ValidationError, BusinessRuleError

class CadastroBrindesScreen(BaseFormScreen):
    """Tela de cadastro de brindes seguindo o padrão de fornecedores"""
    
    def __init__(self, parent, user_manager, on_success=None):
        """Inicializa a tela de cadastro de brindes"""
        super().__init__(
            parent=parent,
            user_manager=user_manager,
            title="Cadastro de Brindes",
            subtitle="Preencha os dados do brinde",
            on_success=on_success
        )
        self.filial_checkboxes = {}
        self.filial_entries = {}
        
    def setup_base_ui(self):
        """Configura a interface base do formulário"""
        super().setup_base_ui()

        # Cria o frame rolável que servirá como o form_frame
        self.form_frame = ctk.CTkScrollableFrame(self.frame)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Agora, cria o título DENTRO do form_frame
        self.create_section_title(self.title, 0, self.subtitle)

        # O resto da configuração continua normalmente
        self.create_form_fields()
        self.load_defaults()
        self.create_buttons()
    
    def create_form_fields(self):
        """Cria os campos do formulário"""
        row = 0
        
        # Descrição
        self.create_field_entry(
            "Descrição *", "descricao", row, 
            placeholder="Ex: Caneta Azul BIC", required=True
        )
        row += 1
        
        # Categoria
        self.create_field_combobox(
            "Categoria *", "categoria", row,
            options=self._safe_get_categorias(), required=True
        )
        row += 1
        
        # Quantidade Total
        self.create_field_entry(
            "Quantidade Total *", "quantidade", row,
            placeholder="0", required=True, field_type="number"
        )
        row += 1
        
        # Valor Unitário
        self.create_field_entry(
            "Valor Unitário (R$) *", "valor_unitario", row,
            placeholder="0,00", required=True, field_type="number"
        )
        row += 1
        
        # Unidade de Medida
        self.create_field_combobox(
            "Unidade de Medida *", "unidade_medida", row,
            options=self._safe_get_unidades_medida(), required=True
        )
        row += 1
        
        # Fornecedor
        self.create_field_combobox(
            "Fornecedor", "fornecedor", row,
            options=self._safe_get_fornecedor_names(), required=False
        )
        row += 1
        
        # Alocação por Filial
        self.create_filial_allocation_section(row)
    
    def create_field_entry(self, label, key, row, placeholder="", required=False, field_type="text"):
        """Cria um campo de entrada"""
        # Container do campo
        field_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="ew", pady=8, padx=10)
        field_container.grid_columnconfigure(0, weight=1)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_container,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            field_container,
            placeholder_text=placeholder,
            height=35,
            font=ctk.CTkFont(size=11)
        )
        entry.grid(row=1, column=0, sticky="ew")
        
        # Bind para atualizar total se for campo quantidade
        if key == 'quantidade':
            entry.bind("<KeyRelease>", self.on_quantity_change)
        
        # Armazenar referência
        self.field_widgets[key] = {
            'widget': entry,
            'type': field_type,
            'required': required,
            'label': label
        }
    
    def create_field_combobox(self, label, key, row, options=None, required=False):
        """Cria um campo combobox"""
        if options is None:
            options = []
            
        # Container do campo
        field_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        field_container.grid(row=row, column=0, sticky="ew", pady=8, padx=10)
        field_container.grid_columnconfigure(0, weight=1)
        
        # Label
        label_widget = ctk.CTkLabel(
            field_container,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Combobox
        combobox = ctk.CTkComboBox(
            field_container,
            values=options,
            height=35,
            font=ctk.CTkFont(size=11),
            state="readonly"
        )
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
    
    def create_filial_allocation_section(self, row):
        """Cria a seção de alocação por filial"""
        # Container principal
        filial_container = ctk.CTkFrame(self.form_frame)
        filial_container.grid(row=row, column=0, sticky="nsew", pady=15, padx=10)
        filial_container.grid_columnconfigure(0, weight=1)
        filial_container.grid_rowconfigure(2, weight=1)  # Permite que o frame expanda
        
        # Título da seção
        title_label = ctk.CTkLabel(
            filial_container,
            text="Distribuição por Filial *",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Subtítulo explicativo
        subtitle_label = ctk.CTkLabel(
            filial_container,
            text="Selecione as filiais e informe a quantidade para cada uma. A soma deve ser igual à quantidade total.",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50"),
            anchor="w",
            wraplength=600
        )
        subtitle_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        
        # Frame scrollável para as filiais - expandir verticalmente
        filiais_scroll_frame = ctk.CTkScrollableFrame(filial_container, height=200)
        filiais_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        filiais_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Cabeçalho
        header_filial = ctk.CTkLabel(
            filiais_scroll_frame,
            text="Filial",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        header_filial.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        header_quantidade = ctk.CTkLabel(
            filiais_scroll_frame,
            text="Quantidade",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        header_quantidade.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Criar checkboxes e entries para cada filial
        filiais = self._safe_get_filial_names()
        for i, filial in enumerate(filiais, 1):
            # Checkbox da filial
            checkbox = ctk.CTkCheckBox(
                filiais_scroll_frame,
                text=filial,
                font=ctk.CTkFont(size=11),
                command=lambda f=filial: self.on_filial_checkbox_change(f)
            )
            checkbox.grid(row=i, column=0, padx=10, pady=2, sticky="w")
            
            # Entry para quantidade
            entry = ctk.CTkEntry(
                filiais_scroll_frame,
                placeholder_text="0",
                width=100,
                height=30,
                font=ctk.CTkFont(size=11),
                state="disabled"
            )
            entry.grid(row=i, column=1, padx=10, pady=2, sticky="w")
            entry.bind("<KeyRelease>", self.on_quantity_change)
            
            # Armazenar referências
            self.filial_checkboxes[filial] = checkbox
            self.filial_entries[filial] = entry
        
        # Label de total
        self.total_label = ctk.CTkLabel(
            filial_container,
            text="Total alocado: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#00AE9D", "#00AE9D")
        )
        self.total_label.grid(row=3, column=0, sticky="e", padx=15, pady=(0, 15))
    
    def on_filial_checkbox_change(self, filial):
        """Callback quando checkbox de filial é alterado"""
        checkbox = self.filial_checkboxes[filial]
        entry = self.filial_entries[filial]
        
        if checkbox.get():
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, "0")
        else:
            entry.configure(state="disabled")
            entry.delete(0, "end")
        
        self.update_total_allocation()
    
    def on_quantity_change(self, event=None):
        """Callback quando quantidade é alterada"""
        self.update_total_allocation()
    
    def update_total_allocation(self):
        """Atualiza o total alocado"""
        total = 0
        for filial, entry in self.filial_entries.items():
            if self.filial_checkboxes[filial].get():
                try:
                    value = entry.get().strip()
                    if value:
                        total += int(value)
                except ValueError:
                    pass
        
        self.total_label.configure(text=f"Total alocado: {total}")
        
        # Verificar se bate com quantidade total
        try:
            quantidade_total = int(self.field_widgets['quantidade']['widget'].get() or 0)
            if total == quantidade_total and total > 0:
                self.total_label.configure(text_color=("#00AE9D", "#00AE9D"))
            elif total > quantidade_total:
                self.total_label.configure(text_color=("#cc3333", "#cc3333"))
            else:
                self.total_label.configure(text_color=("gray50", "gray50"))
        except ValueError:
            pass
    
    def create_buttons(self):
        """Cria os botões do formulário"""
        # Frame dos botões - fixo no rodapé
        buttons_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
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
    
    def load_defaults(self):
        """Carrega valores padrão"""
        try:
            user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
            if user and user.get('filial'):
                filial_nome = user.get('filial')
                if filial_nome in self.filial_checkboxes:
                    # Pré-selecionar a filial do usuário
                    self.filial_checkboxes[filial_nome].select()
                    self.filial_entries[filial_nome].configure(state="normal")
                    self.filial_entries[filial_nome].delete(0, "end")
                    self.filial_entries[filial_nome].insert(0, "0")
        except Exception as e:
            print(f"Erro ao carregar padrões: {e}")
    
    def get_form_data(self):
        """Obtém os dados do formulário"""
        data = {}
        
        # Campos simples
        for key, field_info in self.field_widgets.items():
            widget = field_info['widget']
            if field_info['type'] == 'combobox':
                data[key] = widget.get()
            else:
                data[key] = widget.get().strip()
        
        # Alocação por filial
        filial_allocation = {}
        for filial, checkbox in self.filial_checkboxes.items():
            if checkbox.get():
                try:
                    quantidade = int(self.filial_entries[filial].get() or 0)
                    if quantidade > 0:
                        filial_allocation[filial] = quantidade
                except ValueError:
                    pass
        
        data['filial'] = filial_allocation
        
        return data
    
    def validate_form(self):
        """Valida o formulário"""
        errors = []
        data = self.get_form_data()
        
        # Validar campos obrigatórios
        for key, field_info in self.field_widgets.items():
            if field_info['required']:
                value = data.get(key, '').strip()
                if not value:
                    field_name = key.replace('_', ' ').title()
                    errors.append(f"O campo '{field_name}' é obrigatório")
        
        # Validar números
        try:
            if data.get('quantidade'):
                quantidade = int(data['quantidade'])
                if quantidade <= 0:
                    errors.append("Quantidade deve ser um número positivo")
        except ValueError:
            errors.append("Quantidade deve ser um número válido")
        
        try:
            if data.get('valor_unitario'):
                valor = float(data['valor_unitario'].replace(',', '.'))
                if valor <= 0:
                    errors.append("Valor unitário deve ser positivo")
        except ValueError:
            errors.append("Valor unitário deve ser um número válido")
        
        # Validar alocação de filiais
        if not data.get('filial'):
            errors.append("Selecione pelo menos uma filial para alocação")
        else:
            total_alocado = sum(data['filial'].values())
            try:
                quantidade_total = int(data.get('quantidade', 0))
                if total_alocado != quantidade_total:
                    errors.append(f"A soma das quantidades por filial ({total_alocado}) deve ser igual à quantidade total ({quantidade_total})")
            except (ValueError, TypeError):
                errors.append("Quantidade total inválida")
        
        return errors
    
    def save(self):
        """Salva o brinde"""
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Erro de Validação", "\n".join(errors))
            return
        
        data = self.get_form_data()
        
        try:
            # Validar dados com o validador
            BrindeValidator.validate(data)
            
            # Se chegou aqui, os dados são válidos
            messagebox.showinfo("Sucesso", "Brinde salvo com sucesso!")
            
            if self.on_success:
                self.on_success()
                
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except BusinessRuleError as e:
            messagebox.showerror("Regra de Negócio", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao salvar o brinde: {str(e)}")
    
    def cancel(self):
        """Cancela o cadastro"""
        if self.has_data():
            if not messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar? Todas as alterações serão perdidas."):
                return
        
        self.destroy()
    
    def has_data(self):
        """Verifica se há dados no formulário"""
        data = self.get_form_data()
        return any(data.values())
    
    def clear_form(self):
        """Limpa o formulário"""
        # Limpar campos de entrada
        for field_info in self.field_widgets.values():
            widget = field_info['widget']
            if field_info['type'] == 'combobox':
                widget.set("")
            else:
                widget.delete(0, "end")
        
        # Limpar checkboxes e entradas de filiais
        for filial, checkbox in self.filial_checkboxes.items():
            checkbox.deselect()
            entry = self.filial_entries[filial]
            entry.configure(state="disabled")
            entry.delete(0, "end")
        
        # Atualizar total
        self.update_total_allocation()
    
    def _safe_get_categorias(self):
        """Obtém categorias de forma segura"""
        try:
            return [cat['nome'] for cat in data_provider.get_categorias()]
        except Exception:
            return []
    
    def _safe_get_unidades_medida(self):
        """Obtém unidades de medida de forma segura"""
        try:
            return [unidade['nome'] for unidade in data_provider.get_unidades_medida()]
        except Exception:
            return ["UN"]
    
    def _safe_get_fornecedor_names(self):
        """Obtém nomes de fornecedores de forma segura"""
        try:
            return [""] + [f["nome"] for f in data_provider.get_fornecedores()]
        except Exception:
            return [""]
    
    def _safe_get_filial_names(self):
        """Obtém nomes de filiais de forma segura"""
        try:
            return [f["nome"] for f in data_provider.get_filiais()]
        except Exception:
            return ["Matriz"]
