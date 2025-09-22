"""
Tela de Gestão de Brindes
"""

import customtkinter as ctk
from tkinter import messagebox
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
        section_frame, content_frame = self.create_section("📋 Lista de Brindes")
        
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
        
        # Tabela de brindes (mock)
        self.create_brindes_table(content_frame)
    
    def create_brindes_table(self, parent):
        """Cria a tabela de brindes com paginação"""
        # Frame da tabela
        self.table_frame = ctk.CTkFrame(parent)
        self.table_frame.pack(fill="both", expand=True)
        
        # Carregar dados se necessário
        if not self.current_brindes:
            self.current_brindes = data_provider.get_brindes()
            self.filtered_brindes = self.current_brindes.copy()
        
        # Calcular paginação
        self.calculate_pagination()
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(self.table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        headers = ["Código", "Descrição", "Categoria", "Quantidade", "Valor Unit.", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # Frame para conteúdo da tabela (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(self.table_frame, height=400)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        qty = str(brinde.get('quantidade', 0))
        valor = f"R$ {brinde.get('valor_unitario', 0):.2f}".replace('.', ',')
        
        row_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Cor da linha baseada no estoque
        bg_color = ("red", "darkred") if int(qty) <= 10 else None
        if bg_color:
            row_frame.configure(fg_color=bg_color)
        
        # Células
        cells = [codigo, desc, cat, qty, valor]
        for j, cell in enumerate(cells):
            label = ctk.CTkLabel(row_frame, text=cell)
            label.grid(row=0, column=j, padx=10, pady=5, sticky="ew")
            
            # Adicionar evento de duplo clique para edição
            label.bind("<Double-Button-1>", lambda e, c=codigo: self.edit_brinde(c))
        
        # Botões de ação
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=5, padx=10, pady=5, sticky="ew")
        
        edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=30, height=25, 
                                command=lambda c=codigo: self.edit_brinde(c))
        edit_btn.pack(side="left", padx=2)
        
        # Botão de exclusão (apenas para administradores)
        if self.user_manager.has_permission('admin'):
            delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=30, height=25,
                                     fg_color="red", hover_color="darkred",
                                     command=lambda c=codigo: self.delete_brinde(c))
            delete_btn.pack(side="left", padx=2)
        
        transfer_btn = ctk.CTkButton(actions_frame, text="↔️", width=30, height=25, 
                                   command=lambda c=codigo: self.transfer_brinde(c))
        transfer_btn.pack(side="left", padx=2)
        
        entry_btn = ctk.CTkButton(actions_frame, text="📥", width=30, height=25, 
                                command=lambda c=codigo: self.entry_brinde(c))
        entry_btn.pack(side="left", padx=2)
        
        exit_btn = ctk.CTkButton(actions_frame, text="📤", width=30, height=25, 
                               command=lambda c=codigo: self.exit_brinde(c))
        exit_btn.pack(side="left", padx=2)
    
    def create_pagination_controls(self):
        """Cria os controles de paginação"""
        pagination_frame = ctk.CTkFrame(self.table_frame)
        pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Informações da paginação
        info_label = ctk.CTkLabel(
            pagination_frame, 
            text=f"Página {self.current_page} de {self.total_pages} | "
                 f"Mostrando {len(self.filtered_brindes)} itens | "
                 f"{self.items_per_page} por página"
        )
        info_label.pack(side="left", padx=10, pady=10)
        
        # Botões de navegação
        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
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
                'type': 'combobox',
                'required': True,
                'options': data_provider.get_filiais()
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
                data_provider.get_filiais()
            )
            
            # Adicionar usuário atual
            user = self.user_manager.get_current_user()
            if user:
                validated_data['usuario_cadastro'] = user.get('username', 'admin')
            
            # Criar brinde
            brinde = data_provider.create_brinde(validated_data)
            
            # Atualizar listagem
            self.refresh_brindes_list()
            
            messagebox.showinfo("Sucesso", "Entrada de estoque realizada com sucesso!")
            
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except BusinessRuleError as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar entrada: {e}")
    
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
                'options': data_provider.get_filiais()
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            f"✏️ Editar Brinde - {codigo}",
            fields,
            on_submit=lambda data: self.save_edit_brinde(brinde['id'], data)
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
                data_provider.get_filiais()
            )
            
            # Atualizar brinde
            brinde = data_provider.update_brinde(brinde_id, validated_data)
            
            if brinde:
                # Atualizar listagem
                self.refresh_brindes_list()
                messagebox.showinfo("Sucesso", f"Brinde '{brinde['descricao']}' atualizado com sucesso!")
                return True
            else:
                messagebox.showerror("Erro", "Brinde não encontrado")
                return False
                
        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar brinde: {e}")
            return False
    
    def transfer_brinde(self, codigo):
        """Transfere um brinde"""
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
            messagebox.showerror("Erro", "Não há estoque disponível para transferência")
            return
        
        # Obter filiais disponíveis (exceto a atual)
        filiais_disponiveis = [f for f in data_provider.get_filiais() if f != brinde.get('filial')]
        
        if not filiais_disponiveis:
            messagebox.showerror("Erro", "Não há filiais disponíveis para transferência")
            return
        
        fields = [
            {
                'key': 'quantidade',
                'label': f'Quantidade a Transferir (Disponível: {brinde.get("quantidade", 0)})',
                'type': 'number',
                'required': True,
                'placeholder': '0',
                'validation': 'positive_number'
            },
            {
                'key': 'filial_destino',
                'label': 'Filial de Destino',
                'type': 'combobox',
                'required': True,
                'options': filiais_disponiveis
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
            f"↔️ Transferir - {brinde['descricao']} ({codigo})",
            fields,
            on_submit=lambda data: self.save_transfer_brinde(brinde, data)
        )
        dialog.show()
    
    def save_transfer_brinde(self, brinde, data):
        """Salva transferência de brinde"""
        try:
            # Validar dados de transferência
            validated_data = MovimentacaoValidator.validate_transferencia_data(
                data, 
                brinde.get('quantidade', 0),
                data_provider.get_filiais(),
                brinde.get('filial', 'Matriz')
            )
            
            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            filial_origem = brinde.get('filial', 'Matriz')
            filial_destino = validated_data['filial_destino']
            quantidade_transfer = validated_data['quantidade']
            
            # Criar movimentação de saída na filial origem
            movimentacao_saida = {
                'brinde_id': brinde['id'],
                'brinde_codigo': brinde['codigo'],
                'brinde_descricao': brinde['descricao'],
                'tipo': 'transferencia_saida',
                'quantidade': quantidade_transfer,
                'usuario': user.get('username', 'admin') if user else 'admin',
                'justificativa': validated_data['justificativa'],
                'filial': filial_origem,
                'filial_destino': filial_destino
            }
            
            # Atualizar estoque (diminuir na origem)
            data_provider.update_estoque_brinde(brinde['id'], quantidade_transfer, 'saida')
            
            # Verificar se já existe o mesmo brinde na filial destino
            brindes_destino = data_provider.get_brindes(filial_destino)
            brinde_destino = None
            
            for b in brindes_destino:
                if (b.get('descricao') == brinde['descricao'] and 
                    b.get('categoria') == brinde.get('categoria') and
                    b.get('filial') == filial_destino):
                    brinde_destino = b
                    break
            
            if brinde_destino:
                # Atualizar estoque do brinde existente na filial destino
                data_provider.update_estoque_brinde(brinde_destino['id'], quantidade_transfer, 'entrada')
                
                # Criar movimentação de entrada na filial destino
                movimentacao_entrada = {
                    'brinde_id': brinde_destino['id'],
                    'brinde_codigo': brinde_destino['codigo'],
                    'brinde_descricao': brinde_destino['descricao'],
                    'tipo': 'transferencia_entrada',
                    'quantidade': quantidade_transfer,
                    'usuario': user.get('username', 'admin') if user else 'admin',
                    'justificativa': f"Transferência de {filial_origem}",
                    'filial': filial_destino,
                    'filial_origem': filial_origem
                }
            else:
                # Criar novo brinde na filial destino
                novo_brinde_data = {
                    'descricao': brinde['descricao'],
                    'categoria': brinde['categoria'],
                    'quantidade': quantidade_transfer,
                    'valor_unitario': brinde.get('valor_unitario', 0),
                    'unidade_medida': brinde.get('unidade_medida', 'UN'),
                    'filial': filial_destino,
                    'usuario_cadastro': user.get('username', 'admin') if user else 'admin'
                }
                
                novo_brinde = data_provider.create_brinde(novo_brinde_data)
                
                # Criar movimentação de entrada na filial destino
                movimentacao_entrada = {
                    'brinde_id': novo_brinde['id'],
                    'brinde_codigo': novo_brinde['codigo'],
                    'brinde_descricao': novo_brinde['descricao'],
                    'tipo': 'transferencia_entrada',
                    'quantidade': quantidade_transfer,
                    'usuario': user.get('username', 'admin') if user else 'admin',
                    'justificativa': f"Transferência de {filial_origem}",
                    'filial': filial_destino,
                    'filial_origem': filial_origem
                }
            
            # Registrar movimentações
            data_provider.create_movimentacao(movimentacao_saida)
            data_provider.create_movimentacao(movimentacao_entrada)
            
            # Atualizar listagem
            self.refresh_brindes_list()
            
            messagebox.showinfo(
                "Sucesso", 
                f"Transferência realizada com sucesso!\n\n"
                f"Item: {brinde['descricao']}\n"
                f"Quantidade: {quantidade_transfer}\n"
                f"De: {filial_origem}\n"
                f"Para: {filial_destino}"
            )
            return True
            
        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao realizar transferência: {e}")
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
        # Encontrar e destruir tabela existente
        for widget in self.frame.winfo_children():
            if hasattr(widget, '_table_frame'):
                widget.destroy()
                break
        
        # Recriar seção de listagem
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
                messagebox.showerror("Erro", "Brinde não encontrado!")
                return
            
            # Confirmar exclusão
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o brinde:\n\n"
                f"Código: {brinde.get('codigo')}\n"
                f"Descrição: {brinde.get('descricao')}\n"
                f"Quantidade: {brinde.get('quantidade')}\n\n"
                f"Esta ação não pode ser desfeita!"
            )
            
            if not resposta:
                return
            
            # Verificar se há movimentações associadas
            movimentacoes = data_provider.get_movimentacoes(brinde_id=brinde.get('id'))
            if movimentacoes:
                messagebox.showerror(
                    "Exclusão Bloqueada",
                    "Não é possível excluir este brinde pois existem movimentações associadas.\n"
                    "Para manter a integridade dos dados, brindes com histórico não podem ser excluídos."
                )
                return
            
            # Excluir brinde
            sucesso = data_provider.delete_brinde(brinde.get('id'))
            
            if sucesso:
                messagebox.showinfo("Sucesso", "Brinde excluído com sucesso!")
                self.refresh_brindes_list()
            else:
                messagebox.showerror("Erro", "Erro ao excluir brinde!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir brinde: {e}")
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.refresh_brindes_list()
