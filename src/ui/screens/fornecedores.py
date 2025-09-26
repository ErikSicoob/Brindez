"""
Tela de Gestão de Fornecedores
"""

import customtkinter as ctk
from tkinter import messagebox
from .base_screen import BaseScreen
from ...data.data_provider import data_provider
from ...utils.validators import Validators, ValidationError
from ..components.form_dialog import FormDialog
from .cadastro_fornecedor import CadastroFornecedorScreen

class FornecedoresScreen(BaseScreen):
    """Tela de gestão de fornecedores"""
    
    def __init__(self, parent, user_manager):
        """Inicializa a tela de fornecedores"""
        super().__init__(parent, user_manager, "Fornecedores")
        self.current_fornecedores = []
        self.filtered_fornecedores = []
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface da tela"""
        # Título
        self.create_title("🏢 Gestão de Fornecedores", "Cadastro e controle de fornecedores")
        
        # Seção de controles
        self.create_controls_section()
        
        # Seção de listagem
        self.create_listing_section()
        
        # Carregar dados iniciais
        self.load_fornecedores()
    
    def create_controls_section(self):
        """Cria a seção de controles"""
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.pack(fill="x", pady=(0, 15))
        controls_frame.grid_columnconfigure(1, weight=1)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=0, sticky="w", padx=15, pady=15)
        
        # Botão Novo Fornecedor
        new_button = ctk.CTkButton(
            buttons_frame,
            text="➕ Novo Fornecedor",
            command=self.new_fornecedor,
            height=40,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82")
        )
        new_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Botão Atualizar
        refresh_button = ctk.CTkButton(
            buttons_frame,
            text="🔄 Atualizar",
            command=self.load_fornecedores,
            height=40,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82")
        )
        refresh_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Campo de busca
        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew", padx=15, pady=15)
        search_frame.grid_columnconfigure(0, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="🔍 Buscar:", font=ctk.CTkFont(size=12, weight="bold"))
        search_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Digite o nome, código ou contato do fornecedor...",
            height=35
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="🔍",
            command=self.search_fornecedores,
            width=40,
            height=35,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82")
        )
        search_button.grid(row=1, column=1)
    
    def create_listing_section(self):
        """Cria a seção de listagem"""
        listing_frame = ctk.CTkFrame(self.frame)
        listing_frame.pack(fill="both", expand=True)
        listing_frame.grid_columnconfigure(0, weight=1)
        listing_frame.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho da lista
        header_frame = ctk.CTkFrame(listing_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        headers = ["Código", "Nome", "Contato", "Telefone", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Lista scrollável
        self.list_frame = ctk.CTkScrollableFrame(listing_frame)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.list_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Paginação
        self.pagination_frame = ctk.CTkFrame(listing_frame, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
    
    def load_fornecedores(self):
        """Carrega a lista de fornecedores"""
        try:
            fornecedores_result = data_provider.get_fornecedores()
            
            # Verificar se o resultado é uma lista
            if not isinstance(fornecedores_result, list):
                print(f"Erro: get_fornecedores() retornou {type(fornecedores_result)} ao invés de list")
                self.current_fornecedores = []
                self.filtered_fornecedores = []
            else:
                self.current_fornecedores = fornecedores_result
                self.filtered_fornecedores = self.current_fornecedores.copy()
            
            self.update_pagination()
            self.display_fornecedores()
            print(f"Carregados {len(self.current_fornecedores)} fornecedores")
        except Exception as e:
            print(f"Erro ao carregar fornecedores: {e}")
            self.current_fornecedores = []
            self.filtered_fornecedores = []
            self.update_pagination()
            self.display_fornecedores()
            messagebox.showerror("Erro", f"Erro ao carregar fornecedores: {e}")
    
    def display_fornecedores(self):
        """Exibe os fornecedores na lista"""
        # Limpar lista atual
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Calcular itens da página atual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_fornecedores = self.filtered_fornecedores[start_idx:end_idx]
        
        if not page_fornecedores:
            # Mensagem quando não há fornecedores
            no_data_label = ctk.CTkLabel(
                self.list_frame,
                text="📋 Nenhum fornecedor encontrado",
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray50")
            )
            no_data_label.grid(row=0, column=0, columnspan=5, pady=50)
            return
        
        # Exibir fornecedores
        for i, fornecedor in enumerate(page_fornecedores):
            self.create_fornecedor_row(i, fornecedor)
        
        self.update_pagination_controls()
    
    def create_fornecedor_row(self, row, fornecedor):
        """Cria uma linha para um fornecedor"""
        # Alternar cor de fundo
        bg_color = ("gray90", "gray20") if row % 2 == 0 else ("white", "gray15")
        
        row_frame = ctk.CTkFrame(self.list_frame, fg_color=bg_color)
        row_frame.grid(row=row, column=0, columnspan=5, sticky="ew", pady=1, padx=5)
        row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Código
        codigo_label = ctk.CTkLabel(
            row_frame,
            text=fornecedor.get('codigo', 'N/A'),
            font=ctk.CTkFont(size=11, weight="bold")
        )
        codigo_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        
        # Nome
        nome_label = ctk.CTkLabel(
            row_frame,
            text=fornecedor.get('nome', 'N/A'),
            font=ctk.CTkFont(size=11)
        )
        nome_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        
        # Contato
        contato_label = ctk.CTkLabel(
            row_frame,
            text=fornecedor.get('contato_nome', 'N/A'),
            font=ctk.CTkFont(size=11)
        )
        contato_label.grid(row=0, column=2, padx=10, pady=8, sticky="w")
        
        # Telefone
        telefone_label = ctk.CTkLabel(
            row_frame,
            text=fornecedor.get('telefone', 'N/A'),
            font=ctk.CTkFont(size=11)
        )
        telefone_label.grid(row=0, column=3, padx=10, pady=8, sticky="w")
        
        # Botões de ação
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, padx=10, pady=5, sticky="e")
        
        # Botão Editar
        edit_button = ctk.CTkButton(
            actions_frame,
            text="✏️",
            command=lambda f=fornecedor: self.edit_fornecedor(f),
            width=30,
            height=25,
            fg_color=("#00AE9D", "#00AE9D"),
            hover_color=("#008f82", "#008f82")
        )
        edit_button.grid(row=0, column=0, padx=2)
        
        # Botão Excluir
        delete_button = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda f=fornecedor: self.delete_fornecedor(f),
            width=30,
            height=25,
            fg_color=("#cc3333", "#cc3333"),
            hover_color=("#a82828", "#a82828")
        )
        delete_button.grid(row=0, column=1, padx=2)
    
    def update_pagination(self):
        """Atualiza informações de paginação"""
        total_items = len(self.filtered_fornecedores)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = 1
    
    def update_pagination_controls(self):
        """Atualiza os controles de paginação"""
        # Limpar controles existentes
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        
        if self.total_pages <= 1:
            return
        
        # Informações da página
        info_label = ctk.CTkLabel(
            self.pagination_frame,
            text=f"Página {self.current_page} de {self.total_pages} ({len(self.filtered_fornecedores)} fornecedores)",
            font=ctk.CTkFont(size=11)
        )
        info_label.pack(side="left", padx=10)
        
        # Botões de navegação
        nav_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=10)
        
        # Primeira página
        if self.current_page > 1:
            first_button = ctk.CTkButton(
                nav_frame,
                text="⏮️",
                command=lambda: self.go_to_page(1),
                width=30,
                height=25
            )
            first_button.pack(side="left", padx=2)
        
        # Página anterior
        if self.current_page > 1:
            prev_button = ctk.CTkButton(
                nav_frame,
                text="◀️",
                command=lambda: self.go_to_page(self.current_page - 1),
                width=30,
                height=25
            )
            prev_button.pack(side="left", padx=2)
        
        # Próxima página
        if self.current_page < self.total_pages:
            next_button = ctk.CTkButton(
                nav_frame,
                text="▶️",
                command=lambda: self.go_to_page(self.current_page + 1),
                width=30,
                height=25
            )
            next_button.pack(side="left", padx=2)
        
        # Última página
        if self.current_page < self.total_pages:
            last_button = ctk.CTkButton(
                nav_frame,
                text="⏭️",
                command=lambda: self.go_to_page(self.total_pages),
                width=30,
                height=25
            )
            last_button.pack(side="left", padx=2)
    
    def go_to_page(self, page):
        """Navega para uma página específica"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.display_fornecedores()
    
    def on_search_change(self, event=None):
        """Callback para mudança no campo de busca"""
        # Buscar automaticamente após uma pausa
        if hasattr(self, '_search_timer'):
            self.frame.after_cancel(self._search_timer)
        self._search_timer = self.frame.after(500, self.search_fornecedores)
    
    def search_fornecedores(self):
        """Realiza busca de fornecedores"""
        query = self.search_entry.get().strip()
        
        if not query:
            self.filtered_fornecedores = self.current_fornecedores.copy()
        else:
            try:
                self.filtered_fornecedores = data_provider.search_fornecedores(query)
            except Exception as e:
                print(f"Erro na busca: {e}")
                self.filtered_fornecedores = []
        
        self.current_page = 1
        self.update_pagination()
        self.display_fornecedores()
    
    def new_fornecedor(self):
        """Abre tela de cadastro de novo fornecedor"""
        try:
            # Ocultar tela atual
            self.hide()
            
            # Criar e mostrar tela de cadastro
            cadastro_screen = CadastroFornecedorScreen(
                self.parent,
                self.user_manager,
                on_success=self.on_fornecedor_saved
            )
            cadastro_screen.show()
            
        except Exception as e:
            print(f"Erro ao abrir cadastro de fornecedor: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir cadastro de fornecedor: {e}")
    
    def on_fornecedor_saved(self):
        """Callback chamado quando um fornecedor é salvo"""
        # Recarregar dados
        self.load_fornecedores()
        # Mostrar esta tela novamente
        self.show()
    
    def save_new_fornecedor(self, data):
        """Salva um novo fornecedor"""
        try:
            # Validações básicas
            if not data.get('nome', '').strip():
                raise ValidationError("Nome da empresa é obrigatório")
            
            # Validar e-mail se fornecido
            if data.get('email'):
                Validators.validate_email(data['email'], 'E-mail')
            
            # Adicionar usuário atual
            user = self.user_manager.get_current_user()
            if user:
                data['usuario_criacao_id'] = user.get('id', 1)
            
            # Criar fornecedor
            success = data_provider.create_fornecedor(data)
            
            if success:
                messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
                self.load_fornecedores()
                return True
            else:
                messagebox.showerror("Erro", "Erro ao cadastrar fornecedor")
                return False
                
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar fornecedor: {e}")
            return False
    
    def edit_fornecedor(self, fornecedor):
        """Abre tela de edição de fornecedor"""
        try:
            # Ocultar tela atual
            self.hide()
            
            # Criar e mostrar tela de edição
            cadastro_screen = CadastroFornecedorScreen(
                self.parent,
                self.user_manager,
                fornecedor_data=fornecedor,
                on_success=self.on_fornecedor_saved
            )
            cadastro_screen.show()
            
        except Exception as e:
            print(f"Erro ao abrir edição de fornecedor: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir edição de fornecedor: {e}")
    
    def save_edit_fornecedor(self, fornecedor_id, data):
        """Salva edição de fornecedor"""
        try:
            # Validações básicas
            if not data.get('nome', '').strip():
                raise ValidationError("Nome da empresa é obrigatório")
            
            # Validar e-mail se fornecido
            if data.get('email'):
                Validators.validate_email(data['email'], 'E-mail')
            
            # Atualizar fornecedor
            success = data_provider.update_fornecedor(fornecedor_id, data)
            
            if success:
                messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
                self.load_fornecedores()
                return True
            else:
                messagebox.showerror("Erro", "Erro ao atualizar fornecedor")
                return False
                
        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar fornecedor: {e}")
            return False
    
    def delete_fornecedor(self, fornecedor):
        """Exclui um fornecedor"""
        nome = fornecedor.get('nome', 'N/A')
        
        # Confirmar exclusão
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o fornecedor '{nome}'?\n\n"
            "Esta ação não pode ser desfeita.",
            icon="warning"
        )
        
        if result:
            try:
                success = data_provider.delete_fornecedor(fornecedor['id'])
                
                if success:
                    messagebox.showinfo("Sucesso", f"Fornecedor '{nome}' excluído com sucesso!")
                    self.load_fornecedores()
                else:
                    messagebox.showerror("Erro", "Erro ao excluir fornecedor")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir fornecedor: {e}")
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.load_fornecedores()
