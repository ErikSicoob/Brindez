"""
Tela de Gestão de Brindes
"""

import customtkinter as ctk
from tkinter import messagebox
from .base_screen import BaseScreen
from ..components.form_dialog import FormDialog
from ...data.data_provider import data_provider
from ...utils.validators import BrindeValidator, MovimentacaoValidator, ValidationError, BusinessRuleError

class BrindesScreen(BaseScreen):
    """Tela de gestão de brindes"""
    
    def __init__(self, parent, user_manager):
        """Inicializa a tela de brindes"""
        super().__init__(parent, user_manager)
        self.current_brindes = []
        self.filtered_brindes = []
        self.current_page = 1
        self.items_per_page = 10
        self.total_pages = 1
        # Carregar dados iniciais de forma segura
        self._load_initial_data()
        self.setup_ui()
        
    def after(self, ms, func=None, *args):
        """Implementação do método after para agendamento de tarefas"""
        if func is not None:
            # Usar o frame principal para agendar a tarefa
            return self.frame.after(ms, func, *args)
        return None
    
    def _load_initial_data(self):
        """Carrega dados iniciais de forma segura"""
        try:
            raw_data = data_provider.get_brindes()
            # Filtrar apenas objetos válidos
            self.current_brindes = []
            for item in raw_data:
                if item and isinstance(item, dict) and 'codigo' in item and 'descricao' in item:
                    self.current_brindes.append(item)
            
            self.filtered_brindes = self.current_brindes.copy()
            print(f"Dados carregados: {len(self.current_brindes)} brindes válidos")
        except Exception as e:
            print(f"Erro ao carregar dados iniciais: {e}")
            self.current_brindes = []
            self.filtered_brindes = []
    
    def _validate_brinde(self, brinde):
        """Valida se um brinde é um objeto válido"""
        return (brinde and 
                isinstance(brinde, dict) and 
                'codigo' in brinde and 
                'descricao' in brinde and 
                'id' in brinde)
    
    def _safe_get_brindes(self):
        """Obtém brindes de forma segura, filtrando objetos inválidos"""
        try:
            raw_data = data_provider.get_brindes()
            valid_brindes = []
            for item in raw_data:
                if self._validate_brinde(item):
                    valid_brindes.append(item)
                else:
                    print(f"Brinde inválido ignorado: {item}")
            return valid_brindes
        except Exception as e:
            print(f"Erro ao obter brindes: {e}")
            return []
    
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
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Filtro por categoria
        category_label = ctk.CTkLabel(filters_frame, text="📂 Categoria:")
        category_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.category_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todas", "Canetas", "Chaveiros", "Camisetas", "Blocos", "Outros"],
            command=self.on_filter_change
        )
        self.category_combo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por filial
        filial_label = ctk.CTkLabel(filters_frame, text="🏢 Filial:")
        filial_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.filial_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todas", "Matriz", "Filial SP", "Filial RJ", "Filial BH"],
            command=self.on_filter_change
        )
        self.filial_combo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")
        
        # Tabela de brindes
        self.create_brindes_table(content_frame)
    
    def on_search_change(self, event=None):
        """Callback para mudanças no campo de busca"""
        # Usar debounce para evitar muitas chamadas
        if hasattr(self, '_search_timer'):
            self.parent.after_cancel(self._search_timer)
        
        self._search_timer = self.parent.after(500, self.apply_filters)
    
    def on_filter_change(self, value=None):
        """Callback para mudanças nos filtros de categoria e filial"""
        self.apply_filters()
    
    def apply_filters(self):
        """Aplica todos os filtros de forma otimizada"""
        try:
            # Começar com todos os brindes válidos
            self.filtered_brindes = [b for b in self.current_brindes if self._validate_brinde(b)]
            
            # Obter valores dos filtros de forma segura
            search_text = ""
            categoria = "Todas"
            filial = "Todas"
            
            if hasattr(self, 'search_entry') and self.search_entry.winfo_exists():
                search_text = self.search_entry.get().strip().lower()
            
            if hasattr(self, 'category_combo') and self.category_combo.winfo_exists():
                categoria = self.category_combo.get()
            
            if hasattr(self, 'filial_combo') and self.filial_combo.winfo_exists():
                filial = self.filial_combo.get()
            
            # Aplicar filtros
            if search_text:
                self.filtered_brindes = [
                    b for b in self.filtered_brindes 
                    if search_text in str(b.get('codigo', '')).lower() or 
                       search_text in str(b.get('descricao', '')).lower()
                ]
            
            if categoria and categoria != "Todas":
                self.filtered_brindes = [b for b in self.filtered_brindes if b.get('categoria') == categoria]
            
            if filial and filial != "Todas":
                self.filtered_brindes = [b for b in self.filtered_brindes if b.get('filial') == filial]
            
            # Consolidar por item pai (descrição): somar quantidades e manter um código representativo
            from collections import defaultdict
            totals_by_desc = defaultdict(int)
            first_by_desc = {}
            for b in self.filtered_brindes:
                desc_key = str(b.get('descricao', '')).strip().lower()
                if not desc_key:
                    continue
                try:
                    totals_by_desc[desc_key] += int(b.get('quantidade', 0) or 0)
                except Exception:
                    pass
                if desc_key not in first_by_desc:
                    first_by_desc[desc_key] = b

            display_list = []
            self._aggregated_code_map = {}
            for desc_key, total_qty in totals_by_desc.items():
                rep = first_by_desc[desc_key]
                display_list.append({
                    'id': rep.get('id'),
                    'codigo': rep.get('codigo'),
                    'descricao': rep.get('descricao'),
                    'categoria': rep.get('categoria'),
                    'valor_unitario': rep.get('valor_unitario', 0),
                    'quantidade': total_qty,
                    'filial': '—',
                })
                self._aggregated_code_map[desc_key] = rep.get('codigo')

            self.filtered_brindes = display_list

            # Resetar para primeira página
            self.current_page = 1
            
        except Exception as e:
            print(f"Erro ao aplicar filtros: {e}")
            self.filtered_brindes = [b for b in self.current_brindes if self._validate_brinde(b)]
    
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
            raw_data = data_provider.get_brindes()
            # Filtrar valores None ou inválidos
            self.current_brindes = [b for b in raw_data if b and isinstance(b, dict)]
            self.filtered_brindes = self.current_brindes.copy()
        
        # Calcular paginação
        self.calculate_pagination()
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(self.table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", pady=(0, 2))
        
        # Configurar pesos das colunas
        columns = 6  # Total de colunas
        for i in range(columns):
            header_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Cabeçalhos
        headers = [
            "Código", 
            "Descrição", 
            "Categoria", 
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
        try:
            # Verificar se brinde é válido
            if not brinde or not isinstance(brinde, dict):
                print(f"ERRO: Brinde inválido na linha {row_index}: {brinde} (tipo: {type(brinde)})")
                return
                
            codigo = brinde.get('codigo', '')
            desc = brinde.get('descricao', '')
            cat = brinde.get('categoria', '')
            qty = brinde.get('quantidade', 0)
            valor_unit = brinde.get('valor_unitario', 0)
        except Exception as e:
            print(f"ERRO em create_brinde_row linha {row_index}: {e}")
            print(f"Brinde problemático: {brinde}")
            return
        
        # Formatar valores monetários
        valor_unit_fmt = f"R$ {valor_unit:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
        valor_total = qty * valor_unit
        valor_total_fmt = f"R$ {valor_total:,.2f}".replace('.', '|').replace(',', '.').replace('|', ',')
        
        # Criar frame da linha
        row_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)
        
        # Configurar colunas
        for i in range(6):  # 6 colunas
            row_frame.columnconfigure(i, weight=1, uniform="col")
        
        # Dados da linha
        cells = [
            codigo,
            desc,
            cat,
            f"{qty}",
            valor_unit_fmt,
            valor_total_fmt
        ]
        
        # Adicionar células
        for col, text in enumerate(cells):
            # Alinhamento: esquerda para texto, direita para números
            anchor = "w" if col < 3 else "e"
                
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                anchor=anchor,
                font=ctk.CTkFont(size=12)
            )
            label.grid(row=0, column=col, padx=5, pady=3, sticky="nsew")
            
            # Adicionar eventos de clique usando o código representativo do item pai
            try:
                desc_key = str(desc).strip().lower()
                rep_codigo = self._aggregated_code_map.get(desc_key, codigo)
            except Exception:
                rep_codigo = codigo
            label.bind("<Button-1>", lambda e, c=rep_codigo: self.edit_brinde(c))  # Clique esquerdo para editar
            label.bind("<Button-3>", lambda e, c=rep_codigo: self.show_context_menu_at_cursor(e, c))  # Clique direito para menu
        
        # Adicionar evento de clique direito no frame da linha também usando código representativo
        try:
            desc_key_frame = str(desc).strip().lower()
            rep_codigo_frame = self._aggregated_code_map.get(desc_key_frame, codigo)
        except Exception:
            rep_codigo_frame = codigo
        row_frame.bind("<Button-3>", lambda e, c=rep_codigo_frame: self.show_context_menu_at_cursor(e, c))
        
        # Destacar linhas com estoque baixo
        if int(qty) <= 10:
            row_frame.configure(fg_color=("#ffdddd", "#550000"))
    
    def show_context_menu_at_cursor(self, event, codigo):
        """Mostra o menu de contexto na posição do cursor"""
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            # Criar menu usando tkinter nativo (mais compatível)
            menu = tk.Menu(self.frame, tearoff=0, bg="white", fg="black", 
                          activebackground="lightblue", activeforeground="black",
                          font=("Arial", 10))
            
            # Função para fechar o menu de forma segura
            def close_menu():
                try:
                    menu.unpost()
                except:
                    pass
            
            # Adicionar itens do menu
            menu.add_command(
                label="✏️ Editar", 
                command=lambda: [close_menu(), self.edit_brinde(codigo)]
            )
            
            # Botão Excluir (sempre presente, mas com verificação interna)
            menu.add_command(
                label="🗑️ Excluir", 
                command=lambda: [close_menu(), self.delete_brinde(codigo)]
            )
            
            menu.add_separator()
            
            menu.add_command(
                label="🔄 Transferir", 
                command=lambda: [close_menu(), self.transfer_brinde(codigo)]
            )
            menu.add_command(
                label="📥 Entrada", 
                command=lambda: [close_menu(), self.entry_brinde(codigo)]
            )
            menu.add_command(
                label="📤 Saída", 
                command=lambda: [close_menu(), self.exit_brinde(codigo)]
            )
            
            # Mostrar menu na posição do cursor
            try:
                menu.tk_popup(event.x_root, event.y_root)
                
                # Capturar eventos para fechar o menu
                menu.bind("<FocusOut>", lambda e: close_menu())
                menu.bind("<Escape>", lambda e: close_menu())
                
                # Forçar o foco para o menu
                menu.focus_set()
                
            except Exception as e:
                print(f"Erro ao exibir menu: {e}")
                close_menu()
                
        except Exception as e:
            print(f"Erro ao criar menu de contexto: {e}")
            try:
                messagebox.showerror("Erro", "Não foi possível exibir o menu de contexto")
            except:
                pass
    
    
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
        self.safe_refresh_table()
    
    def go_to_previous_page(self):
        """Vai para a página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.safe_refresh_table()
    
    def go_to_next_page(self):
        """Vai para a próxima página"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.safe_refresh_table()
    
    def go_to_last_page(self):
        """Vai para a última página"""
        self.current_page = self.total_pages
        self.safe_refresh_table()
    
    def go_to_page(self, page):
        """Vai para uma página específica"""
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.safe_refresh_table()
    
    def refresh_table(self):
        """Atualiza a tabela de forma otimizada"""
        try:
            # Recalcular paginação
            self.calculate_pagination()
            
            # Renderizar página atual
            self.render_current_page()
            
            # Recriar controles de paginação
            self.create_pagination_controls()
        except Exception as e:
            print(f"Erro ao atualizar tabela: {e}")
            self.create_listing_section()

    def refresh_brindes_list(self):
        """Recarrega a lista de brindes de forma otimizada"""
        try:
            # Recarregar dados
            raw_brindes = data_provider.get_brindes()
            
            # Filtrar dados válidos
            self.current_brindes = [b for b in raw_brindes if self._validate_brinde(b)]
            
            # Aplicar filtros e atualizar interface
            self.apply_filters()
            self.refresh_table()
            
        except Exception as e:
            print(f"Erro ao recarregar brindes: {e}")
            self.create_listing_section()
    

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
        dialog.show({'filial': user_filial or brinde.get('filial')})
    
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

            # Atualização imediata e otimizada
            self.refresh_brindes_list()

            messagebox.showinfo("Sucesso", "Brinde(s) cadastrado(s) com sucesso!")

        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
        except BusinessRuleError as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar brinde: {e}")
    
    def safe_refresh_table(self):
        """Método unificado para atualização segura da tabela"""
        self.refresh_table()
    
    def edit_brinde(self, codigo):
        """Edita um brinde"""
        # Encontrar brinde pelo código de forma segura
        brinde = None
        for b in self.current_brindes:
            if self._validate_brinde(b) and b.get('codigo') == codigo:
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
            brinde_atualizado = data_provider.update_brinde(brinde_id, validated_data)
            
            if brinde_atualizado:
                # Atualização imediata
                self.refresh_brindes_list()
                messagebox.showinfo("Sucesso", "Brinde atualizado com sucesso!")
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
        # Encontrar o brinde clicado para obter a descrição de forma segura
        brinde_clicado = None
        for b in self.current_brindes:
            if self._validate_brinde(b) and b.get('codigo') == codigo:
                brinde_clicado = b
                break
        
        if not brinde_clicado:
            messagebox.showerror("Erro", "Brinde não encontrado.")
            return

        # Encontrar todas as instâncias deste brinde em todas as filiais
        descricao_brinde = brinde_clicado['descricao']
        brindes_em_estoque = [b for b in self.current_brindes if self._validate_brinde(b) and b.get('descricao') == descricao_brinde and b.get('quantidade', 0) > 0]

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

            # Atualização imediata após transferência
            self.refresh_brindes_list()
            
            messagebox.showinfo("Sucesso", f"Transferência realizada: {quantidade_transfer} {descricao_brinde} de {filial_origem_nome} para {filial_destino_nome}")

        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
            return False

    def entry_brinde(self, codigo):
        """Entrada de estoque"""
        # Encontrar brinde pelo código de forma segura
        brinde = None
        for b in self.current_brindes:
            if self._validate_brinde(b) and b.get('codigo') == codigo:
                brinde = b
                break
        
        if not brinde:
            messagebox.showerror("Erro", "Brinde não encontrado")
            return
        
        # Definir filiais acessíveis de acordo com o perfil
        user = self.user_manager.get_current_user() if self.user_manager else None
        user_filial = user.get('filial') if user else brinde.get('filial')
        try:
            todas_filiais = [f['nome'] for f in data_provider.get_filiais()]
        except Exception:
            todas_filiais = [brinde.get('filial')]
        accessible_filiais = todas_filiais
        try:
            if self.user_manager and not self.user_manager.is_admin() and user_filial:
                accessible_filiais = [user_filial]
        except Exception:
            pass

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
                'key': 'filial',
                'label': 'Filial',
                'type': 'combobox',
                'required': True,
                'options': accessible_filiais
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
        
        # Pré-preencher valor unitário atual e filial padrão
        dialog.show({
            'valor_unitario': f"{brinde.get('valor_unitario', 0):.2f}".replace('.', ','),
            'filial': user_filial or brinde.get('filial')
        })
    
    def save_entry_brinde(self, brinde, data):
        """Salva entrada de estoque"""
        try:
            # Validar dados de entrada
            validated_data = MovimentacaoValidator.validate_entrada_data(data)
            
            # Selecionar filial alvo respeitando permissão do usuário
            user = self.user_manager.get_current_user() if self.user_manager else None
            selected_filial = (data.get('filial') or brinde.get('filial'))
            if self.user_manager and not self.user_manager.is_admin() and user:
                selected_filial = user.get('filial', selected_filial)

            # Encontrar ou criar o brinde na filial selecionada
            target_brinde = brinde
            if selected_filial and selected_filial != brinde.get('filial'):
                try:
                    candidatos = data_provider.get_brindes(filial_filter=selected_filial)
                    target_brinde = next((b for b in candidatos if str(b.get('descricao','')).strip().lower() == str(brinde.get('descricao','')).strip().lower()), None)
                except Exception:
                    target_brinde = None
                if not target_brinde:
                    novo_brinde_data = {
                        'descricao': brinde['descricao'],
                        'categoria': brinde['categoria'],
                        'quantidade': 0,
                        'valor_unitario': brinde.get('valor_unitario', 0),
                        'unidade_medida': brinde['unidade_medida'],
                        'filial': selected_filial,
                        'usuario_cadastro': user.get('username', 'admin') if user else 'admin'
                    }
                    target_brinde = data_provider.create_brinde(novo_brinde_data)

            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            
            movimentacao_data = {
                'brinde_id': target_brinde['id'],
                'brinde_codigo': target_brinde.get('codigo', brinde.get('codigo')),
                'brinde_descricao': target_brinde.get('descricao', brinde.get('descricao')),
                'tipo': 'entrada',
                'quantidade': validated_data['quantidade'],
                'usuario': user.get('username', 'admin') if user else 'admin',
                'observacoes': validated_data.get('observacoes', ''),
                'filial': selected_filial or target_brinde.get('filial', 'Matriz')
            }
            
            # Atualizar valor unitário se fornecido
            if validated_data.get('valor_unitario'):
                novo_valor = validated_data['valor_unitario']
                if novo_valor != target_brinde.get('valor_unitario', 0):
                    movimentacao_data['valor_unitario_anterior'] = target_brinde.get('valor_unitario', 0)
                    movimentacao_data['valor_unitario_novo'] = novo_valor
                    # Atualizar valor no brinde
                    data_provider.update_brinde(target_brinde['id'], {**target_brinde, 'valor_unitario': novo_valor})
            
            # Criar movimentação
            movimentacao = data_provider.create_movimentacao(movimentacao_data)
            
            if movimentacao:
                # Atualização imediata
                self.refresh_brindes_list()
                messagebox.showinfo("Sucesso", f"Entrada registrada: +{validated_data['quantidade']} {movimentacao_data['brinde_descricao']} na filial {movimentacao_data['filial']}")
                return True
            
        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar entrada: {e}")
            return False
    
    def exit_brinde(self, codigo):
        """Saída de estoque"""
        # Encontrar brinde pelo código de forma segura
        brinde = None
        for b in self.current_brindes:
            if self._validate_brinde(b) and b.get('codigo') == codigo:
                brinde = b
                break
        
        if not brinde:
            messagebox.showerror("Erro", "Brinde não encontrado")
            return
        
        # Verificar se há estoque disponível
        if brinde.get('quantidade', 0) <= 0:
            messagebox.showerror("Erro", "Não há estoque disponível para este item")
            return
        
        # Definir filiais acessíveis de acordo com o perfil
        user = self.user_manager.get_current_user() if self.user_manager else None
        user_filial = user.get('filial') if user else brinde.get('filial')
        try:
            todas_filiais = [f['nome'] for f in data_provider.get_filiais()]
        except Exception:
            todas_filiais = [brinde.get('filial')]
        accessible_filiais = todas_filiais
        try:
            if self.user_manager and not self.user_manager.is_admin() and user_filial:
                accessible_filiais = [user_filial]
        except Exception:
            pass

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
            },
            {
                'key': 'filial',
                'label': 'Filial',
                'type': 'combobox',
                'required': True,
                'options': accessible_filiais
            }
        ]
        
        dialog = FormDialog(
            self.frame,
            f"📤 Saída de Estoque - {brinde['descricao']} ({codigo})",
            fields,
            on_submit=lambda data: self.save_exit_brinde(brinde, data)
        )
        dialog.show({'filial': user_filial or brinde.get('filial')})
    
    def save_exit_brinde(self, brinde, data):
        """Salva saída de estoque"""
        try:
            # Determinar filial alvo respeitando permissão
            user = self.user_manager.get_current_user() if self.user_manager else None
            selected_filial = (data.get('filial') or brinde.get('filial'))
            if self.user_manager and not self.user_manager.is_admin() and user:
                selected_filial = user.get('filial', selected_filial)

            # Encontrar o brinde correto na filial alvo
            target_brinde = brinde
            if selected_filial and selected_filial != brinde.get('filial'):
                try:
                    candidatos = data_provider.get_brindes(filial_filter=selected_filial)
                    target_brinde = next((b for b in candidatos if str(b.get('descricao','')).strip().lower() == str(brinde.get('descricao','')).strip().lower()), None)
                except Exception:
                    target_brinde = None
            if not target_brinde:
                raise BusinessRuleError("Item não existe na filial selecionada.")

            # Validar dados de saída com estoque da filial alvo
            validated_data = MovimentacaoValidator.validate_saida_data(
                data, target_brinde.get('quantidade', 0)
            )
            
            # Preparar dados da movimentação
            user = self.user_manager.get_current_user()
            
            movimentacao_data = {
                'brinde_id': target_brinde['id'],
                'brinde_codigo': target_brinde.get('codigo', brinde.get('codigo')),
                'brinde_descricao': target_brinde.get('descricao', brinde.get('descricao')),
                'tipo': 'saida',
                'quantidade': validated_data['quantidade'],
                'usuario': user.get('username', 'admin') if user else 'admin',
                'justificativa': validated_data['justificativa'],
                'destino': validated_data.get('destino', ''),
                'filial': selected_filial or target_brinde.get('filial', 'Matriz')
            }
            
            # Criar movimentação
            movimentacao = data_provider.create_movimentacao(movimentacao_data)
            
            # Atualizar listagem
            self.refresh_brindes_list()
            
            novo_estoque = target_brinde['quantidade'] - validated_data['quantidade']
            messagebox.showinfo(
                "Sucesso", 
                f"Saída registrada com sucesso!\n\n"
                f"Item: {target_brinde['descricao']} (Filial {movimentacao_data['filial']})\n"
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
    
    
    
    def delete_brinde(self, codigo):
        """Exclui um brinde (apenas administradores)"""
        try:
            # Verificar permissão de administrador
            if not self.user_manager.has_permission('admin'):
                messagebox.showerror("Acesso Negado", "Apenas administradores podem excluir brindes.")
                return
            
            # Recarregar dados frescos do banco de forma segura
            fresh_brindes = self._safe_get_brindes()
            
            # Buscar brinde nos dados frescos
            brinde_para_excluir = None
            for brinde in fresh_brindes:
                if self._validate_brinde(brinde) and str(brinde.get('codigo', '')).strip() == str(codigo).strip():
                    brinde_para_excluir = brinde
                    break
            
            if not brinde_para_excluir:
                messagebox.showerror("Erro", f"Brinde '{codigo}' não encontrado")
                return
            
            brinde_id = brinde_para_excluir.get('id')
            descricao = brinde_para_excluir.get('descricao', f'Código {codigo}')
            
            if not brinde_id:
                messagebox.showerror("Erro", "ID do brinde não encontrado")
                return
            
            # Confirmar exclusão
            if messagebox.askyesno("Confirmar Exclusão", f"Excluir '{descricao}'?"):
                # Excluir do banco
                if data_provider.delete_brinde(brinde_id):
                    # Atualização imediata e otimizada
                    self.refresh_brindes_list()
                    
                    # Mostrar mensagem de sucesso
                    messagebox.showinfo("Sucesso", f"'{descricao}' excluído com sucesso!")
                else:
                    messagebox.showerror("Erro", "Falha na exclusão")
                    
        except Exception as e:
            print(f"ERRO delete_brinde: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", "Erro interno na exclusão")
    
    def force_refresh_interface(self):
        """Força atualização completa da interface"""
        def _refresh():
            try:
                self.refresh_brindes_list()
            except Exception as e:
                print(f"Erro ao atualizar interface: {e}")
                self.create_listing_section()
        
        # Agendar atualização
        self.frame.after(100, _refresh)
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.refresh_brindes_list()

    def cancel_current_form(self):
        """Cancela o formulário atual"""
        pass
