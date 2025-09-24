"""
Tela de Estoque de Brindes - Visualização consolidada por item
"""

import customtkinter as ctk
from tkinter import messagebox
from .base_screen import BaseScreen
from ...data.data_provider import data_provider
from collections import defaultdict

class EstoqueBrindesScreen(BaseScreen):
    """Tela de estoque consolidado de brindes"""
    
    def __init__(self, parent, user_manager):
        """Inicializa a tela de estoque de brindes"""
        super().__init__(parent, user_manager)
        self.current_estoque = []
        self.filtered_estoque = []
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self.tooltip = None
        # Carregar dados iniciais
        self._load_initial_data()
        self.setup_ui()
        
    def show_tooltip(self, widget, text):
        """Exibe uma dica de ferramenta próximo ao widget"""
        if self.tooltip:
            self.tooltip.destroy()
            
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        
        self.tooltip = ctk.CTkToplevel(self.frame)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            self.tooltip,
            text=text,
            fg_color="#333333",
            text_color="white",
            corner_radius=4,
            padx=10,
            pady=5,
            wraplength=300
        )
        label.pack()
        
        # Fechar tooltip quando o mouse sair
        widget.bind("<Leave>", lambda e: self.hide_tooltip())
    
    def hide_tooltip(self):
        """Remove a dica de ferramenta"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        
    def _load_initial_data(self):
        """Carrega dados iniciais consolidados"""
        try:
            self._consolidate_estoque()
            print(f"Estoque consolidado carregado: {len(self.current_estoque)} itens únicos")
        except Exception as e:
            print(f"Erro ao carregar estoque consolidado: {e}")
            self.current_estoque = []
            self.filtered_estoque = []
    
    def _consolidate_estoque(self):
        """Consolida o estoque por item e filial (uma linha por filial)"""
        try:
            # Obter todos os brindes (respeitando restrição de filial para não-admin e não-global)
            filial_filter = None
            try:
                user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
                if user and not self.user_manager.is_admin():
                    user_filial_nome = user.get('filial')
                    # Determinar se é global (filial número '00')
                    is_global = False
                    try:
                        all_filiais = data_provider.get_filiais() or []
                        fil = next((f for f in all_filiais if f.get('nome') == user_filial_nome), None)
                        if fil and str(fil.get('numero')).zfill(2) == '00':
                            is_global = True
                    except Exception:
                        # fallback para nome 'Matriz'
                        is_global = (user_filial_nome == 'Matriz')
                    if not is_global:
                        filial_filter = user_filial_nome
            except Exception:
                filial_filter = None

            all_brindes = data_provider.get_brindes(filial_filter=filial_filter)
            
            # Agrupar por (descricao, filial)
            per_filial = {}
            for brinde in all_brindes:
                if not brinde or not isinstance(brinde, dict):
                    continue
                descricao = brinde.get('descricao', '')
                filial = brinde.get('filial', 'N/A')
                if not descricao:
                    continue
                key = (descricao.strip().lower(), str(filial))
                if key not in per_filial:
                    per_filial[key] = {
                        'descricao': descricao,
                        'categoria': brinde.get('categoria', ''),
                        'filial': filial,
                        'valor_unitario': brinde.get('valor_unitario', 0),
                        'unidade_medida': brinde.get('unidade_medida', ''),
                        'quantidade_filial': 0,
                        'valor_total_filial': 0,
                        'codigo_exemplo': brinde.get('codigo', ''),
                    }
                per_filial[key]['quantidade_filial'] += int(brinde.get('quantidade', 0) or 0)
            
            # Calcular valor total por filial e preparar lista
            result = []
            for item in per_filial.values():
                item['valor_total_filial'] = item['quantidade_filial'] * (item.get('valor_unitario') or 0)
                result.append(item)
            
            self.current_estoque = result
            self.filtered_estoque = self.current_estoque.copy()
            
        except Exception as e:
            print(f"Erro ao consolidar estoque: {e}")
            self.current_estoque = []
            self.filtered_estoque = []
    
    def setup_ui(self):
        """Configura a interface de estoque de brindes"""
        # Título da tela
        self.create_title("📦 Estoque de Brindes", "Visualização consolidada por item")
        
        # Seção de filtros
        self.create_filters_section()
        
        # Seção de listagem
        self.create_listing_section()
    
    def create_filters_section(self):
        """Cria a seção de filtros"""
        section_frame, content_frame = self.create_section("🔍 Filtros")
        
        # Frame para filtros
        filters_frame = ctk.CTkFrame(content_frame)
        filters_frame.pack(fill="x", pady=(0, 15))
        filters_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Campo de busca
        search_label = ctk.CTkLabel(filters_frame, text="🔍 Buscar Item:")
        search_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.search_entry = ctk.CTkEntry(filters_frame, placeholder_text="Digite para buscar...")
        self.search_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Filtro por categoria
        category_label = ctk.CTkLabel(filters_frame, text="📂 Categoria:")
        category_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        try:
            categorias_vals = data_provider.get_categorias() or []
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            categorias_vals = []
        self.category_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todas"] + list(categorias_vals),
            command=self.on_filter_change
        )
        self.category_combo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por filial
        filial_label = ctk.CTkLabel(filters_frame, text="🏢 Visualizar Filial:")
        filial_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        try:
            filiais_list = data_provider.get_filiais() or []
        except Exception as e:
            print(f"Erro ao carregar filiais: {e}")
            filiais_list = []
        filiais_nomes = ["Todas"] + [f.get('nome', 'N/A') for f in filiais_list]
        self.filial_combo = ctk.CTkComboBox(
            filters_frame,
            values=filiais_nomes,
            command=self.on_filter_change
        )
        self.filial_combo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Restringir seleção de filial para usuários não-Admin e não-globais
        try:
            user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
            if user and not self.user_manager.is_admin():
                user_filial = user.get('filial')
                # Verificar se filial do usuário é global (numero '00')
                is_global = False
                try:
                    all_filiais = data_provider.get_filiais() or []
                    fil = next((f for f in all_filiais if f.get('nome') == user_filial), None)
                    if fil and str(fil.get('numero')).zfill(2) == '00':
                        is_global = True
                except Exception:
                    is_global = (user_filial == 'Matriz')
                if not is_global:
                    self.filial_combo.configure(values=[user_filial])
                    self.filial_combo.set(user_filial)
                    self.filial_combo.configure(state="disabled")
                else:
                    # Usuário global: padrão "Todas"
                    if "Todas" in self.filial_combo.cget('values'):
                        self.filial_combo.set("Todas")
        except Exception as e:
            print(f"Aviso ao aplicar restrição de filial: {e}")
    
    def on_search_change(self, event=None):
        """Callback para mudanças no campo de busca"""
        if hasattr(self, '_search_timer'):
            self.parent.after_cancel(self._search_timer)
        
        self._search_timer = self.parent.after(500, self.apply_filters)
    
    def on_filter_change(self, value=None):
        """Callback para mudanças nos filtros"""
        self.apply_filters()
    
    def apply_filters(self):
        """Aplica todos os filtros"""
        try:
            # Começar com todos os itens
            self.filtered_estoque = self.current_estoque.copy()
            
            # Obter valores dos filtros
            search_text = ""
            categoria = "Todas"
            filial_filter = "Todas"
            
            if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
                search_text = self.search_entry.get().strip().lower()
            
            if hasattr(self, 'category_combo') and self.category_combo.winfo_exists():
                categoria = self.category_combo.get()
            
            if hasattr(self, 'filial_combo') and self.filial_combo.winfo_exists():
                filial_filter = self.filial_combo.get()
            
            # Aplicar filtro de busca
            if search_text:
                self.filtered_estoque = [
                    item for item in self.filtered_estoque 
                    if search_text in item.get('descricao', '').lower() or 
                       search_text in item.get('categoria', '').lower()
                ]
            
            # Aplicar filtro de categoria
            if categoria and categoria != "Todas":
                self.filtered_estoque = [
                    item for item in self.filtered_estoque 
                    if item.get('categoria') == categoria
                ]
            
            # Aplicar filtro de filial (lista já é por filial)
            if filial_filter and filial_filter != "Todas":
                self.filtered_estoque = [
                    item for item in self.filtered_estoque 
                    if item.get('filial') == filial_filter
                ]
            
            # Resetar para primeira página
            self.current_page = 1
            self.refresh_table()
            
        except Exception as e:
            print(f"Erro ao aplicar filtros: {e}")
            self.filtered_estoque = self.current_estoque.copy()
    
    def create_listing_section(self):
        """Cria a seção de listagem"""
        section_frame, content_frame = self.create_section("📋 Estoque Consolidado por Filial")
        self.listing_section_frame = section_frame
        
        # Criar tabela
        self.create_estoque_table(content_frame)
    
    def create_estoque_table(self, parent):
        """Cria a tabela de estoque consolidado"""
        if hasattr(self, 'table_frame') and self.table_frame.winfo_exists():
            for widget in self.table_frame.winfo_children():
                widget.destroy()
        else:
            self.table_frame = ctk.CTkFrame(parent)
            self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Calcular paginação
        self.calculate_pagination()
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(self.table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", pady=(0, 2))
        
        # Configurar colunas
        columns = 6
        for i in range(columns):
            header_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Cabeçalhos
        headers = [
            "Descrição", 
            "Categoria", 
            "Filial",
            "Quantidade", 
            "Valor Unit.", 
            "Valor Total"
        ]
        
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame, 
                text=header, 
                font=ctk.CTkFont(weight="bold"),
                anchor="center"
            )
            label.grid(row=0, column=col, padx=5, pady=10, sticky="ew")
        
        # Frame para conteúdo da tabela
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()
            
        self.content_frame = ctk.CTkScrollableFrame(
            self.table_frame, 
            height=400,
            fg_color=("gray95", "gray16")
        )
        self.content_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Configurar colunas no conteúdo
        for i in range(columns):
            self.content_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Renderizar página atual
        self.render_current_page()
        
        # Controles de paginação
        self.create_pagination_controls()
    
    def calculate_pagination(self):
        """Calcula informações de paginação"""
        total_items = len(self.filtered_estoque)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
    
    def render_current_page(self):
        """Renderiza os itens da página atual"""
        # Limpar conteúdo anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Calcular índices da página atual
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.filtered_estoque))
        
        # Renderizar itens da página atual
        for i in range(start_idx, end_idx):
            item = self.filtered_estoque[i]
            self.create_item_row(item, i - start_idx)
    
    def create_item_row(self, item, row_index):
        """Cria uma linha da tabela para um item"""
        try:
            # Coagir possíveis None para strings seguras (evita len(None))
            descricao = str(item.get('descricao') or 'Sem descrição')
            categoria = str(item.get('categoria') or 'Sem categoria')
            filial = str(item.get('filial') or 'N/A')
            quantidade = int(item.get('quantidade_filial', 0))
            valor_unitario = float(item.get('valor_unitario', 0))
            valor_total = float(item.get('valor_total_filial', 0))
            
            # Formatar valores monetários
            valor_unit_fmt = f"R$ {valor_unitario:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
            valor_total_fmt = f"R$ {valor_total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
            
            # Criar frame da linha com cor de fundo alternada para melhor legibilidade
            bg_color = ("#f9f9f9", "#1e1e1e") if row_index % 2 == 0 else ("#ffffff", "#2b2b2b")
            row_frame = ctk.CTkFrame(
                self.content_frame, 
                fg_color=bg_color,
                corner_radius=4
            )
            row_frame.pack(fill="x", pady=1, padx=2)
            
            # Configurar colunas
            for i in range(6):
                row_frame.columnconfigure(i, weight=1, uniform="col")
            
            # Dados da linha
            cells = [
                descricao[:50] + ('...' if len(descricao) > 50 else ''),  # Limitar tamanho da descrição
                categoria[:20] + ('...' if len(categoria) > 20 else ''),   # Limitar tamanho da categoria
                filial,
                f"{quantidade:,}".replace(",", "."),  # Formatar número com separador de milhar
                valor_unit_fmt,
                valor_total_fmt
            ]
            
            # Adicionar células
            for col, text in enumerate(cells):
                anchor = "w" if col < 3 else "e"
                padx = (10, 5) if col == 0 else (5, 5)
                
                label = ctk.CTkLabel(
                    row_frame,
                    text=text,
                    anchor=anchor,
                    font=ctk.CTkFont(size=12),
                    text_color=("#000000", "#ffffff"),
                    justify="left" if col < 3 else "right"
                )
                label.grid(row=0, column=col, padx=padx, pady=5, sticky="nsew")
                
                # Adicionar dica de ferramenta com texto completo para campos grandes
                if col in [0, 1] and len(str(text)) > 20:
                    tooltip_text = descricao if col == 0 else categoria
                    label.bind("<Enter>", lambda e, t=tooltip_text, w=label: self.show_tooltip(w, t))
                    label.bind("<Leave>", lambda e: self.hide_tooltip())
                
                # Adicionar evento de clique para mostrar detalhes
                label.bind("<Button-1>", lambda e, i=item: self.show_item_details(i))
            
            # Destacar linhas com estoque baixo
            if quantidade <= 10:
                row_frame.configure(fg_color=("#ffebee", "#3a1f1f"))  # Vermelho mais suave
                
            # Adicionar hover effect
            row_frame.bind("<Enter>", lambda e, f=row_frame: f.configure(fg_color=("#e3f2fd", "#2c3e50")))
            row_frame.bind("<Leave>", lambda e, f=row_frame, b=bg_color: f.configure(fg_color=b))
                
        except Exception as e:
            print(f"Erro ao criar linha {row_index}: {e}")
    
    def show_item_details(self, item):
        """Mostra detalhes do item por filial"""
        try:
            descricao = item.get('descricao', 'Item')
            filiais = item.get('filiais', [])
            
            # Criar janela de detalhes
            detail_window = ctk.CTkToplevel(self.frame)
            detail_window.title(f"Detalhes - {descricao}")
            detail_window.geometry("600x400")
            detail_window.transient(self.frame)
            detail_window.grab_set()
            
            # Centralizar janela
            detail_window.update_idletasks()
            x = (detail_window.winfo_screenwidth() // 2) - (600 // 2)
            y = (detail_window.winfo_screenheight() // 2) - (400 // 2)
            detail_window.geometry(f"600x400+{x}+{y}")
            
            # Título
            title_label = ctk.CTkLabel(
                detail_window, 
                text=f"📦 {descricao}",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=20)
            
            # Frame para informações gerais
            info_frame = ctk.CTkFrame(detail_window)
            info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            info_text = f"""Categoria: {item.get('categoria', 'N/A')}
Valor Unitário: R$ {item.get('valor_unitario', 0):,.2f}
Quantidade Total: {item.get('quantidade_total', 0)}
Valor Total: R$ {item.get('valor_total', 0):,.2f}"""
            
            info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left")
            info_label.pack(pady=15)
            
            # Frame para detalhes por filial
            filiais_frame = ctk.CTkFrame(detail_window)
            filiais_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            filiais_label = ctk.CTkLabel(
                filiais_frame, 
                text="Distribuição por Filial:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            filiais_label.pack(pady=(15, 10))
            
            # Lista de filiais
            filiais_scrollable = ctk.CTkScrollableFrame(filiais_frame)
            filiais_scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            for filial_info in filiais:
                filial_frame = ctk.CTkFrame(filiais_scrollable)
                filial_frame.pack(fill="x", pady=2)
                
                filial_text = f"🏢 {filial_info['nome']}: {filial_info['quantidade']} unidades (Código: {filial_info['codigo']})"
                filial_label = ctk.CTkLabel(filial_frame, text=filial_text, anchor="w")
                filial_label.pack(padx=10, pady=5, fill="x")
            
            # Botão fechar
            close_btn = ctk.CTkButton(
                detail_window,
                text="Fechar",
                command=detail_window.destroy
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            print(f"Erro ao mostrar detalhes: {e}")
            messagebox.showerror("Erro", "Não foi possível exibir os detalhes do item")
    
    def create_pagination_controls(self):
        """Cria os controles de paginação"""
        if hasattr(self, 'pagination_frame') and self.pagination_frame.winfo_exists():
            self.pagination_frame.destroy()
            
        self.pagination_frame = ctk.CTkFrame(self.table_frame)
        self.pagination_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Informações da paginação
        info_label = ctk.CTkLabel(
            self.pagination_frame, 
            text=f"Página {self.current_page} de {self.total_pages} | "
                 f"Mostrando {len(self.filtered_estoque)} linhas | "
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
        
        # Páginas numeradas
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
        try:
            self.calculate_pagination()
            self.render_current_page()
            self.create_pagination_controls()
        except Exception as e:
            print(f"Erro ao atualizar tabela: {e}")
    
    def refresh_data(self):
        """Recarrega os dados"""
        try:
            self._consolidate_estoque()
            self.apply_filters()
        except Exception as e:
            print(f"Erro ao recarregar dados: {e}")
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.refresh_data()
