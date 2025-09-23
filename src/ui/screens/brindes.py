"""
Tela de Gestão de Brindes
"""

import customtkinter as ctk
from tkinter import messagebox, Menu as tkMenu
from .base_screen import BaseScreen
from ..components.form_dialog import FormDialog
from ...data.data_provider import data_provider
from ...utils.user_manager import UserManager
from ...utils.validators import BrindeValidator, MovimentacaoValidator, ValidationError, BusinessRuleError

class BrindesScreen(BaseScreen):
    """Tela de gestão de brindes"""
    
    def __init__(self, parent):
        """Inicializa a tela de brindes"""
        super().__init__(parent, "Brindes")
        self.user_manager = UserManager()
        self.current_brindes = []
        self.filtered_brindes = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface de brindes"""
        # Título da tela
        self.create_title("🎁 Gestão de Brindes", "Cadastro, edição e controle de brindes")
        
        # Seção de ações rápidas
        self.create_actions_section()
        
        # Seção de listagem
        self.create_listing_section()
    
    def create_actions_section(self):
        """Cria a seção de ações rápidas"""
        section_frame, content_frame = self.create_section("⚡ Ações Rápidas")
        
        # Frame para botões
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Botão Novo Brinde
        new_button = ctk.CTkButton(
            buttons_frame,
            text="➕ Novo Brinde",
            command=self.new_brinde,
            height=40
        )
        new_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Botão Importar
        import_button = ctk.CTkButton(
            buttons_frame,
            text="📥 Importar",
            command=self.import_brindes,
            height=40
        )
        import_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Botão Exportar
        export_button = ctk.CTkButton(
            buttons_frame,
            text="📤 Exportar",
            command=self.export_brindes,
            height=40
        )
        export_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        # Botão Relatório
        report_button = ctk.CTkButton(
            buttons_frame,
            text="📊 Relatório",
            command=self.generate_report,
            height=40
        )
        report_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
    
    def create_listing_section(self):
        """Cria a seção de listagem de brindes"""
        # Se a seção já existe, não recriar
        if hasattr(self, 'listing_section_frame') and self.listing_section_frame.winfo_exists():
            return
            
        # Criar a seção
        section_frame, content_frame = self.create_section("📋 Lista de Brindes")
        self.listing_section_frame = section_frame
        
        # Filtros
        filters_frame = ctk.CTkFrame(content_frame)
        filters_frame.pack(fill="x", pady=(0, 15))
        filters_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Campo de busca
        search_label = ctk.CTkLabel(filters_frame, text="🔍 Buscar:")
        search_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.search_entry = ctk.CTkEntry(filters_frame, placeholder_text="Digite para buscar...")
        self.search_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por categoria
        category_label = ctk.CTkLabel(filters_frame, text="📂 Categoria:")
        category_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.category_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todas", "Canetas", "Chaveiros", "Camisetas", "Blocos", "Outros"]
        )
        self.category_combo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por filial
        filial_label = ctk.CTkLabel(filters_frame, text="🏢 Filial:")
        filial_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.filial_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todas", "Matriz", "Filial SP", "Filial RJ", "Filial BH"]
        )
        self.filial_combo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Tabela de brindes
        self.create_brindes_table(content_frame)
    
    def create_brindes_table(self, parent):
        """Cria a tabela de brindes com paginação"""
        # Se a tabela já existe, apenas atualizamos os dados
        if hasattr(self, 'table_frame') and self.table_frame.winfo_exists():
            # Limpar conteúdo existente
            for widget in self.table_frame.winfo_children():
                widget.destroy()
        else:
            # Se não existe, criamos o frame da tabela
            self.table_frame = ctk.CTkFrame(parent)
            self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Carregar dados se necessário
        if not self.current_brindes:
            self.current_brindes = data_provider.get_brindes()
            self.filtered_brindes = self.current_brindes.copy()
        
        # Calcular paginação
        self.calculate_pagination()
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(self.table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", pady=(0, 2))
        
        # Configurar pesos das colunas
        columns = 7  # Total de colunas
        for i in range(columns):
            header_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Cabeçalhos
        headers = [
            "Código", 
            "Descrição", 
            "Categoria", 
            "Quantidade", 
            "Valor Unit.", 
            "Valor Total",
            "Ações"
        ]
        
        for i, header in enumerate(headers):
            anchor = "w" if i < 3 else "e"  # Alinhar texto à esquerda, números à direita
            if i == len(headers) - 1:  # Última coluna (ações)
                anchor = "center"
                
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=ctk.CTkFont(weight="bold"),
                anchor=anchor
            )
            label.grid(row=0, column=i, padx=5, pady=8, sticky="nsew")
        
        # Frame para conteúdo da tabela (scrollable)
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()
            
        self.content_frame = ctk.CTkScrollableFrame(
            self.table_frame, 
            height=400,
            fg_color=("gray95", "gray16")  # Fundo mais claro/escuro para melhor contraste
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Configurar pesos das colunas no conteúdo
        for i in range(columns):
            self.content_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Renderizar página atual
        self.render_current_page()
        
        # Controles de paginação
        self.create_pagination_controls()
    
    def calculate_pagination(self):
        """Calcula informações de paginação"""
        total_items = len(self.filtered_brindes)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        # Ajustar página atual se necessário
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
    
    def render_current_page(self):
        """Renderiza os itens da página atual"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Calcular índices da página atual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_brindes))
        
        # Renderizar itens da página atual
        for i in range(start_idx, end_idx):
            brinde = self.filtered_brindes[i]
            self.create_brinde_row(brinde, i - start_idx)
    
    def create_brinde_row(self, brinde, row_index):
        """Cria uma linha da tabela para um brinde"""
        codigo = brinde.get('codigo', '')
        desc = brinde.get('descricao', '')
        cat = brinde.get('categoria', '')
        qty = brinde.get('quantidade', 0)
        valor_unit = brinde.get('valor_unitario', 0)
        
        # Formatar valores monetários
        valor_unit_fmt = f"R$ {valor_unit:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
        valor_total = qty * valor_unit
        valor_total_fmt = f"R$ {valor_total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
        
        # Criar frame da linha
        row_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)
        
        # Configurar colunas
        for i in range(7):  # 7 colunas
            row_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Dados da linha
        cells = [
            codigo,
            desc,
            cat,
            f"{qty}",
            valor_unit_fmt,
            valor_total_fmt,
            ""  # Coluna vazia para o botão de menu
        ]
        
        # Adicionar células
        for col, text in enumerate(cells):
            # Alinhamento: esquerda para texto, direita para números
            anchor = "w" if col < 3 else "e"
            if col == 6:  # Última coluna (ações)
                anchor = "center"
                
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                anchor=anchor,
                font=ctk.CTkFont(size=12)
            )
            label.grid(row=0, column=col, padx=5, pady=3, sticky="nsew")
            
            # Adicionar evento de clique para edição
            label.bind("<Button-1>", lambda e, c=codigo: self.edit_brinde(c))
        
        # Adicionar botão de menu de contexto
        menu_btn = ctk.CTkButton(
            row_frame,
            text="⋮",
            width=30,
            height=25,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            command=lambda c=codigo: self.show_context_menu(menu_btn, c)
        )
        menu_btn.grid(row=0, column=6, padx=5, pady=2, sticky="e")
        
        # Destacar linhas com estoque baixo
        if int(qty) <= 10:
            row_frame.configure(fg_color=("#ffdddd", "#550000"))
    
    def show_context_menu(self, widget, codigo):
        """Mostra o menu de contexto para um brinde"""
        # Criar menu
        menu = ctk.CTkMenu(
            self.frame,
            fg_color=("gray90", "gray16"),
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            font=("Arial", 12)
        )
        
        # Adicionar itens do menu
        menu.add_command(
            label="Editar",
            command=lambda: self.edit_brinde(codigo)
        )
        
        if self.user_manager.has_permission('admin'):
            menu.add_command(
                label="Excluir",
                command=lambda: self.delete_brinde(codigo)
            )
        
        menu.add_separator()
        menu.add_command(
            label="Transferir",
            command=lambda: self.transfer_brinde(codigo)
        )
        menu.add_command(
            label="Entrada de Estoque",
            command=lambda: self.entry_brinde(codigo)
        )
        menu.add_command(
            label="Saída de Estoque",
            command=lambda: self.exit_brinde(codigo)
        )
        
        # Mostrar menu
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        menu.tk_popup(x, y)
        menu.grab_set()
    
    def create_context_menu(self, event, codigo):
        """Cria o menu de contexto para ações do brinde"""
        # Criar o menu
        menu = tkMenu(self.frame, tearoff=0)
        
        # Adicionar itens do menu
        menu.add_command(
            label="Editar",
            command=lambda: self.edit_brinde(codigo)
        )
        
        # Apenas administradores podem excluir
        if self.user_manager.has_permission('admin'):
            menu.add_command(
                label="Excluir",
                command=lambda: self.delete_brinde(codigo)
            )
        
        # Adicionar ações de movimentação
        menu.add_separator()
        menu.add_command(
            label="Transferir",
            command=lambda: self.transfer_brinde(codigo)
        )
        menu.add_command(
            label="Entrada de Estoque",
            command=lambda: self.entry_brinde(codigo)
        )
        menu.add_command(
            label="Saída de Estoque",
            command=lambda: self.exit_brinde(codigo)
        )
        
        try:
            # Exibir o menu na posição do clique
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Garantir que o menu seja fechado ao liberar o botão do mouse
            menu.grab_release()
    
    def create_pagination_controls(self):
        """Cria os controles de paginação"""
        # Se já existe um frame de paginação, removê-lo
        if hasattr(self, 'pagination_frame') and self.pagination_frame.winfo_exists():
            self.pagination_frame.destroy()
            
        self.pagination_frame = ctk.CTkFrame(self.table_frame)
        self.pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Informações da paginação
        info_label = ctk.CTkLabel(
            self.pagination_frame, 
            text=f"Página {self.current_page} de {self.total_pages} | "
                 f"Mostrando {len(self.filtered_brindes)} itens | "
                 f"{self.items_per_page} por página"
        )
        info_label.pack(side="left", padx=10, pady=10)
        
        # Botões de navegação
        nav_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=10, pady=10)
        
        # Primeira página
        first_btn = ctk.CTkButton(nav_frame, text="⏮️", width=40, height=30,
                                 command=self.go_to_first_page,
                                 state="disabled" if self.current_page == 1 else "normal")
        first_btn.pack(side="left", padx=2)
        
        # Página anterior
        prev_btn = ctk.CTkButton(nav_frame, text="◀️", width=40, height=30,
                                command=self.go_to_previous_page,
                                state="disabled" if self.current_page == 1 else "normal")
        prev_btn.pack(side="left", padx=2)
        
        # Páginas numeradas (mostrar até 5 páginas)
        start_page = max(1, self.current_page - 2)
        end_page = min(self.total_pages, start_page + 4)
        
        for page in range(start_page, end_page + 1):
            page_btn = ctk.CTkButton(
                nav_frame, 
                text=str(page), 
                width=40, 
                height=30,
                command=lambda p=page: self.go_to_page(p),
                fg_color="blue" if page == self.current_page else None
            )
            page_btn.pack(side="left", padx=2)
        
        # Próxima página
        next_btn = ctk.CTkButton(nav_frame, text="▶️", width=40, height=30,
                                command=self.go_to_next_page,
                                state="disabled" if self.current_page == self.total_pages else "normal")
        next_btn.pack(side="left", padx=2)
        
        # Última página
        last_btn = ctk.CTkButton(nav_frame, text="⏭️", width=40, height=30,
                                command=self.go_to_last_page,
                                state="disabled" if self.current_page == self.total_pages else "normal")
        last_btn.pack(side="left", padx=2)
    
    def go_to_first_page(self):
        """Vai para a primeira página"""
        self.current_page = 1
        self.refresh_table()
    
    def go_to_previous_page(self):
        """Vai para a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_table()
    
    def go_to_next_page(self):
        """Vai para a próxima página"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.refresh_table()
    
    def go_to_last_page(self):
        """Vai para a última página"""
        self.current_page = self.total_pages
        self.refresh_table()
    
    def go_to_page(self, page):
        """Vai para uma página específica"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.refresh_table()
    
    def refresh_table(self):
        """Atualiza a tabela"""
        # Limpar controles de paginação existentes
        for widget in self.table_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.content_frame:
                # Manter apenas o cabeçalho
                if not any(isinstance(child, ctk.CTkLabel) and child.cget("font").cget("weight") == "bold" 
                          for child in widget.winfo_children()):
                    widget.destroy()
        
        # Recalcular paginação
        self.calculate_pagination()
        
        # Renderizar página atual
        self.render_current_page()
        
        # Recriar controles de paginação
        self.create_pagination_controls()

    def refresh_brindes_list(self):
        """Recarrega a lista de brindes e atualiza a interface"""
        try:
            # Recarregar dados
            self.current_brindes = data_provider.get_brindes()
            self.filtered_brindes = self.current_brindes.copy()
            
            # Verificar se a tabela existe antes de atualizar
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                # Manter a página atual se possível
                current_page = self.current_page
                self.refresh_table()
                
                # Verificar se a página atual ainda é válida
                if current_page > self.total_pages:
                    self.current_page = self.total_pages
                
                # Forçar a renderização da página atual
                self.render_current_page()
            else:
                # Se a tabela não existe, recriar completamente
                self.create_brindes_table(self.listing_section_frame)
                
        except Exception as e:
            print(f"Erro ao atualizar lista de brindes: {e}")

    def new_brinde(self):
        """Abre formulário de novo brinde"""
        fields = [
            {
                'key': 'descricao',
                'label': 'Descrição',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: Caneta Azul BIC'
            },
            {
                'key': 'categoria',
                'label': 'Categoria',
                'type': 'combobox',
                'required': True,
                'options': data_provider.get_categorias()
            },
            {
                'key': 'quantidade',
                'label': 'Quantidade',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_number'
            },
            {
                'key': 'valor_unitario',
                'label': 'Valor Unitário (R$)',
                'type': 'number',
                'required': True,
                'placeholder': '0,00',
                'validation': 'positive_number'
            },
            {
                'key': 'unidade_medida',
                'label': 'Unidade de Medida',
                'type': 'combobox',
                'required': True,
                'options': data_provider.get_unidades_medida()
            },
            {
                'key': 'filial',
                'label': 'Filial',
                'type': 'checkbox_group',
                'required': True,
                'options': [f['nome'] for f in data_provider.get_filiais()]
            },
            {
                'key': 'dividir_estoque',
                'label': 'Dividir em partes iguais',
                'type': 'checkbox',
                'required': False
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            "➕ Novo Brinde",
            fields,
            on_submit=self.save_new_brinde
        )
        dialog.show()
    
    def save_new_brinde(self, data):
        """Salva um novo brinde"""
        try:
            # Validar dados usando o validador específico
            validated_data = BrindeValidator.validate_brinde_data(
                data,
                data_provider.get_categorias(),
                data_provider.get_unidades_medida(),
                [f['nome'] for f in data_provider.get_filiais()]
            )

            # Adicionar usuário atual
            user = self.user_manager.get_current_user()
            if user:
                validated_data['usuario_cadastro'] = user.get('username', 'admin')

            filiais_selecionadas = validated_data.pop('filial', [])
            dividir_estoque = validated_data.pop('dividir_estoque', False)
            quantidade_total = int(validated_data.get('quantidade', 0))

            if not filiais_selecionadas:
                raise ValidationError("Pelo menos uma filial deve ser selecionada.")

            if dividir_estoque and len(filiais_selecionadas) > 1:
                quantidade_por_filial = quantidade_total // len(filiais_selecionadas)
                resto = quantidade_total % len(filiais_selecionadas)
            else:
                quantidade_por_filial = quantidade_total
                resto = 0

            for i, filial in enumerate(filiais_selecionadas):
                brinde_data = validated_data.copy()
                brinde_data['filial'] = filial
                
                if dividir_estoque and len(filiais_selecionadas) > 1:
                    brinde_data['quantidade'] = quantidade_por_filial
                    if i == 0 and resto > 0:
                        brinde_data['quantidade'] += resto
                
                # Criar brinde
                data_provider.create_brinde(brinde_data)

            # Atualizar listagem
            self.current_brindes = data_provider.get_brindes()  # Recarregar todos os brindes
            self.filtered_brindes = self.current_brindes.copy()

            # Reconstruir a tabela para refletir as mudanças
            if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                # Manter a página atual se possível
                current_page = self.current_page
                self.refresh_table()

                # Verificar se a página atual ainda é válida
                if current_page > self.total_pages:
                    self.current_page = self.total_pages

                # Forçar a renderização da página atual
                self.render_current_page()

            messagebox.showinfo("Sucesso", "Brinde(s) cadastrado(s) com sucesso!")

        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except BusinessRuleError as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar brinde: {e}")
    
    def edit_brinde(self, codigo):
        """Edita um brinde"""
        # Encontrar brinde pelo código
        brinde = None
        for b in self.current_brindes:
            if b.get('codigo') == codigo:
                brinde = b
                break
        
        if not brinde:
            messagebox.showerror("Erro", "Brinde não encontrado")
            return
        
        fields = [
            {
                'key': 'descricao',
                'label': 'Descrição',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: Caneta Azul BIC'
            },
            {
                'key': 'categoria',
                'label': 'Categoria',
                'type': 'combobox',
                'required': True,
                'options': data_provider.get_categorias()
            },
            {
                'key': 'quantidade',
                'label': 'Quantidade',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_number'
            },
            {
                'key': 'valor_unitario',
                'label': 'Valor Unitário (R$)',
                'type': 'number',
                'required': True,
                'placeholder': '0,00',
                'validation': 'positive_number'
            },
            {
                'key': 'unidade_medida',
                'label': 'Unidade de Medida',
                'type': 'combobox',
                'required': True,
                'options': data_provider.get_unidades_medida()
            },
            {
                'key': 'filial',
                'label': 'Filial',
                'type': 'combobox',
                'required': True,
                'options': [f['nome'] for f in data_provider.get_filiais()]
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            f"✏️ Editar Brinde - {codigo}",
            fields,
            on_submit=lambda data: self.save_edit_brinde(brinde['id'], data),
            on_cancel=self.cancel_current_form
        )
        dialog.show(brinde)
    
    def save_edit_brinde(self, brinde_id, data):
        """Salva edição de um brinde"""
        try:
            # Validar dados usando o validador específico
            validated_data = BrindeValidator.validate_brinde_data(
                data,
                data_provider.get_categorias(),
                data_provider.get_unidades_medida(),
                [f['nome'] for f in data_provider.get_filiais()]
            )
            
            # Atualizar brinde
            brinde = data_provider.update_brinde(brinde_id, validated_data)
            
            if brinde:
                # Atualizar listagem
                self.current_brindes = data_provider.get_brindes()  # Recarregar todos os brindes
                self.filtered_brindes = self.current_brindes.copy()
                
                # Reconstruir a tabela para refletir as mudanças
                if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                    # Manter a página atual
                    current_page = self.current_page
                    self.refresh_table()
                    
                    # Verificar se a página atual ainda é válida
                    if current_page > self.total_pages:
                        self.current_page = self.total_pages
                    
                    # Forçar a renderização da página atual
                    self.render_current_page()
                
                messagebox.showinfo("Sucesso", f"Brinde '{brinde['descricao']}' atualizado com sucesso!")
                return True
            else:
                messagebox.showerror("Erro", "Brinde não encontrado")
                return False
                
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except BusinessRuleError as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar brinde: {e}")
            return False
    
    def transfer_brinde(self, codigo):
        """Abre o formulário de transferência de brinde"""
        # Encontrar o brinde clicado para obter a descrição
        brinde_clicado = next((b for b in self.current_brindes if b.get('codigo') == codigo), None)
        if not brinde_clicado:
            messagebox.showerror("Erro", "Brinde não encontrado.")
            return

        # Encontrar todas as instâncias deste brinde em todas as filiais
        descricao_brinde = brinde_clicado['descricao']
        brindes_em_estoque = [b for b in self.current_brindes if b.get('descricao') == descricao_brinde and b.get('quantidade', 0) > 0]

        if not brindes_em_estoque:
            messagebox.showerror("Estoque Insuficiente", f"Não há estoque de '{descricao_brinde}' em nenhuma filial para transferir.")
            return

        # Preparar dados para o formulário
        filiais_origem = [f"{b['filial']} ({b['quantidade']} unid.)" for b in brindes_em_estoque]
        todas_as_filiais = [f['nome'] for f in data_provider.get_filiais()]
        
        estoque_info = "Estoque disponível: " + ", ".join(filiais_origem)

        fields = [
            {
                'key': 'info',
                'label': estoque_info,
                'type': 'label' # Um novo tipo de campo para exibir informação
            },
            {
                'key': 'filial_origem',
                'label': 'Filial de Origem',
                'type': 'combobox',
                'required': True,
                'options': [b['filial'] for b in brindes_em_estoque]
            },
            {
                'key': 'filial_destino',
                'label': 'Filial de Destino',
                'type': 'combobox',
                'required': True,
                'options': todas_as_filiais
            },
            {
                'key': 'quantidade',
                'label': 'Quantidade a Transferir',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_integer'
            },
            {
                'key': 'justificativa',
                'label': 'Justificativa',
                'type': 'textarea',
                'required': True,
                'placeholder': 'Motivo da transferência (obrigatório)'
            }
        ]

        dialog = FormDialog(
            self.frame,
            f"↔️ Transferir - {descricao_brinde}",
            fields,
            on_submit=lambda data: self.save_transfer_brinde(data, brindes_em_estoque)
        )
        dialog.show()

    def save_transfer_brinde(self, data, brindes_em_estoque):
        """Salva a transferência de brinde entre filiais"""
        try:
            # Encontrar o brinde de origem na lista de brindes em estoque
            filial_origem_nome = data['filial_origem']
            brinde_origem = next((b for b in brindes_em_estoque if b['filial'] == filial_origem_nome), None)

            if not brinde_origem:
                raise BusinessRuleError("Filial de origem inválida.")

            # Validar dados da transferência com a lógica de negócio
            validated_data = MovimentacaoValidator.validate_transferencia_data(
                data,
                brinde_origem.get('quantidade', 0),
                [f['nome'] for f in data_provider.get_filiais()],
                filial_origem_nome
            )

            quantidade_transfer = validated_data['quantidade']
            filial_destino_nome = validated_data['filial_destino']

            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            username = user.get('username', 'admin') if user else 'admin'

            # 1. Atualizar estoque na origem (diminuir)
            data_provider.update_estoque_brinde(brinde_origem['id'], quantidade_transfer, 'saida')

            # 2. Registrar movimentação de saída
            data_provider.create_movimentacao({
                'brinde_id': brinde_origem['id'],
                'brinde_codigo': brinde_origem['codigo'],
                'brinde_descricao': brinde_origem['descricao'],
                'tipo': 'transferencia_saida',
                'quantidade': quantidade_transfer,
                'usuario': username,
                'justificativa': validated_data['justificativa'],
                'filial': filial_origem_nome,
                'filial_destino': filial_destino_nome
            })

            # 3. Encontrar ou criar brinde no destino e atualizar estoque
            brinde_destino = data_provider.find_or_create_brinde_for_transfer(
                brinde_origem, filial_destino_nome, username
            )
            data_provider.update_estoque_brinde(brinde_destino['id'], quantidade_transfer, 'entrada')

            # 4. Registrar movimentação de entrada
            data_provider.create_movimentacao({
                'brinde_id': brinde_destino['id'],
                'brinde_codigo': brinde_destino['codigo'],
                'brinde_descricao': brinde_destino['descricao'],
                'tipo': 'transferencia_entrada',
                'quantidade': quantidade_transfer,
                'usuario': username,
                'justificativa': f"Transferência recebida de {filial_origem_nome}",
                'filial': filial_destino_nome,
                'filial_origem': filial_origem_nome
            })

            # Atualizar a UI
            self.refresh_brindes_list()
            messagebox.showinfo("Sucesso", "Transferência realizada com sucesso!")
            return True

        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
            return False

    def entry_brinde(self, codigo):
        """Entrada de estoque"""
        # Encontrar brinde pelo código
        brinde = None
        for b in self.current_brindes:
            if b.get('codigo') == codigo:
                brinde = b
                break
        
        if not brinde:
            messagebox.showerror("Erro", "Brinde não encontrado")
            return
        
        fields = [
            {
                'key': 'quantidade',
                'label': 'Quantidade de Entrada',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_number'
            },
            {
                'key': 'valor_unitario',
                'label': 'Valor Unitário (R$)',
                'type': 'number',
                'required': False,
                'placeholder': f"{brinde.get('valor_unitario', 0):.2f}".replace('.', ',')
            },
            {
                'key': 'observacoes',
                'label': 'Observações',
                'type': 'textarea',
                'required': False,
                'placeholder': 'Motivo da entrada, fornecedor, etc.'
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            f"📥 Entrada de Estoque - {brinde['descricao']} ({codigo})",
            fields,
            on_submit=lambda data: self.save_entry_brinde(brinde, data)
        )
        
        # Pré-preencher valor unitário atual
        dialog.show({'valor_unitario': f"{brinde.get('valor_unitario', 0):.2f}".replace('.', ',')})
    
    def save_entry_brinde(self, brinde, data):
        """Salva entrada de estoque"""
        try:
            # Validar dados de entrada
            validated_data = MovimentacaoValidator.validate_entrada_data(data)
            
            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            
            movimentacao_data = {
                'brinde_id': brinde['id'],
                'brinde_codigo': brinde['codigo'],
                'brinde_descricao': brinde['descricao'],
                'tipo': 'entrada',
                'quantidade': validated_data['quantidade'],
                'usuario': user.get('username', 'admin') if user else 'admin',
                'observacoes': validated_data.get('observacoes', ''),
                'filial': brinde.get('filial', 'Matriz')
            }
            
            # Atualizar valor unitário se fornecido
            if validated_data.get('valor_unitario'):
                novo_valor = validated_data['valor_unitario']
                if novo_valor != brinde.get('valor_unitario', 0):
                    movimentacao_data['valor_unitario_anterior'] = brinde.get('valor_unitario', 0)
                    movimentacao_data['valor_unitario_novo'] = novo_valor
                    # Atualizar valor no brinde
                    data_provider.update_brinde(brinde['id'], {**brinde, 'valor_unitario': novo_valor})
            
            # Criar movimentação
            movimentacao = data_provider.create_movimentacao(movimentacao_data)
            
            # Atualizar listagem
            self.refresh_brindes_list()
            
            messagebox.showinfo(
                "Sucesso", 
                f"Entrada registrada com sucesso!\n\n"
                f"Item: {brinde['descricao']}\n"
                f"Quantidade: +{validated_data['quantidade']}\n"
                f"Novo estoque: {brinde['quantidade'] + validated_data['quantidade']}"
            )
            return True
            
        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar entrada: {e}")
            return False
    
    def exit_brinde(self, codigo):
        """Saída de estoque"""
        # Encontrar brinde pelo código
        brinde = None
        for b in self.current_brindes:
            if b.get('codigo') == codigo:
                brinde = b
                break
        
        if not brinde:
            messagebox.showerror("Erro", "Brinde não encontrado")
            return
        
        # Verificar se há estoque disponível
        if brinde.get('quantidade', 0) <= 0:
            messagebox.showerror("Erro", "Não há estoque disponível para este item")
            return
        
        fields = [
            {
                'key': 'quantidade',
                'label': f'Quantidade de Saída (Disponível: {brinde.get("quantidade", 0)})',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_number'
            },
            {
                'key': 'justificativa',
                'label': 'Justificativa',
                'type': 'textarea',
                'required': True,
                'placeholder': 'Motivo da saída (obrigatório)'
            },
            {
                'key': 'destino',
                'label': 'Destino/Cliente',
                'type': 'entry',
                'required': False,
                'placeholder': 'Para onde vai o item'
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            f"📤 Saída de Estoque - {brinde['descricao']} ({codigo})",
            fields,
            on_submit=lambda data: self.save_exit_brinde(brinde, data)
        )
        dialog.show()
    
    def save_exit_brinde(self, brinde, data):
        """Salva saída de estoque"""
        try:
            # Validar dados de saída
            validated_data = MovimentacaoValidator.validate_saida_data(
                data, brinde.get('quantidade', 0)
            )
            
            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            
            movimentacao_data = {
                'brinde_id': brinde['id'],
                'brinde_codigo': brinde['codigo'],
                'brinde_descricao': brinde['descricao'],
                'tipo': 'saida',
                'quantidade': validated_data['quantidade'],
                'usuario': user.get('username', 'admin') if user else 'admin',
                'justificativa': validated_data['justificativa'],
                'destino': validated_data.get('destino', ''),
                'filial': brinde.get('filial', 'Matriz')
            }
            
            # Criar movimentação
            movimentacao = data_provider.create_movimentacao(movimentacao_data)
            
            # Atualizar listagem
            self.refresh_brindes_list()
            
            novo_estoque = brinde['quantidade'] - validated_data['quantidade']
            messagebox.showinfo(
                "Sucesso", 
                f"Saída registrada com sucesso!\n\n"
                f"Item: {brinde['descricao']}\n"
                f"Quantidade: -{validated_data['quantidade']}\n"
                f"Novo estoque: {novo_estoque}"
            )
            return True
            
        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar saída: {e}")
            return False
    
    def import_brindes(self):
        """Importa brindes"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de importação será implementada em versão futura")
    
    def export_brindes(self):
        """Exporta brindes"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de exportação será implementada em versão futura")
    
    def generate_report(self):
        """Gera relatório"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de relatório será implementada na próxima fase")
    
    def refresh_brindes_list(self):
        """Atualiza a lista de brindes"""
        # Obter filtros atuais
        categoria_filter = getattr(self, 'category_combo', None)
        filial_filter = getattr(self, 'filial_combo', None)
        search_filter = getattr(self, 'search_entry', None)
        
        categoria = categoria_filter.get() if categoria_filter else "Todas"
        filial = filial_filter.get() if filial_filter else "Todas"
        search = search_filter.get() if search_filter else ""
        
        # Buscar brindes
        if search:
            self.current_brindes = data_provider.search_brindes(search, categoria, filial)
        else:
            self.current_brindes = data_provider.get_brindes(filial if filial != "Todas" else None)
            if categoria != "Todas":
                self.current_brindes = [b for b in self.current_brindes if b.get('categoria') == categoria]
        
        # Recriar tabela
        self.recreate_brindes_table()
    
    def recreate_brindes_table(self):
        """Recria a tabela de brindes"""
        # Se a tabela já existe, apenas atualizamos os dados
        if hasattr(self, 'table_frame') and self.table_frame.winfo_exists():
            # Limpar a tabela existente
            for widget in self.table_frame.winfo_children():
                widget.destroy()
            
            # Recriar a tabela vazia
            self.create_brindes_table(self.content_frame.master)  # content_frame.master é o frame que contém a tabela
        else:
            # Se não existe, criar a seção de listagem
            self.create_listing_section()
    
    def delete_brinde(self, codigo):
        """Exclui um brinde (apenas administradores)"""
        try:
            # Verificar permissão de administrador
            if not self.user_manager.has_permission('admin'):
                messagebox.showerror("Acesso Negado", "Apenas administradores podem excluir brindes.")
                return
            
            # Buscar brinde
            brinde = None
            for b in self.current_brindes:
                if b.get('codigo') == codigo:
                    brinde = b
                    break
            
            if not brinde:
                messagebox.showerror("Erro", "Brinde não encontrado")
                return
            
            # Confirmar exclusão
            if messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o brinde '{brinde.get('descricao')}'?",
                icon='warning'
            ):
                # Excluir brinde
                if data_provider.delete_brinde(codigo):
                    # Atualizar listagem
                    self.current_brindes = data_provider.get_brindes()  # Recarregar todos os brindes
                    self.filtered_brindes = self.current_brindes.copy()
                    
                    # Reconstruir a tabela para refletir as mudanças
                    if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
                        # Ajustar a página atual se necessário
                        self.calculate_pagination()
                        if self.current_page > self.total_pages > 0:
                            self.current_page = self.total_pages
                        
                        # Atualizar a tabela
                        self.refresh_table()
                    
                    messagebox.showinfo("Sucesso", "Brinde excluído com sucesso!")
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o brinde")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir brinde: {e}")
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.refresh_brindes_list()

    def cancel_current_form(self):
        """Cancela o formulário atual"""
        pass
