"""
Classe base para telas de listagem com pesquisa e paginação.
"""

import customtkinter as ctk
from tkinter import messagebox
from .base_screen import BaseScreen

class BaseListingScreen(BaseScreen):
    """Classe base para telas de listagem genéricas."""

    def __init__(self, parent, user_manager, title):
        super().__init__(parent, user_manager, title)
        self.items = []
        self.filtered_items = []
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1

    def setup_ui(self):
        """Configura a interface padrão da tela de listagem."""
        self.create_title(f"📊 {self.title}", f"Gerencie os {self.title.lower()} do sistema")
        self._create_controls_section()
        self._create_listing_section()
        self._load_data()

    # --- Métodos de UI (privados) ---
    def _create_controls_section(self):
        """Cria a seção de controles (ações e pesquisa)."""
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.pack(fill="x", pady=(0, 15), padx=10)
        controls_frame.grid_columnconfigure(1, weight=1)

        # Frame para os botões de ação (a ser preenchido pela subclasse)
        self.actions_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.actions_frame.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self._create_action_buttons()

        # Frame para a pesquisa
        search_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text=f"Buscar por {self.title.lower()}...")
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

    def _create_listing_section(self):
        """Cria a seção de listagem com cabeçalho e área de conteúdo."""
        listing_frame = ctk.CTkFrame(self.frame)
        listing_frame.pack(fill="both", expand=True, padx=10, pady=10)
        listing_frame.grid_columnconfigure(0, weight=1)
        listing_frame.grid_rowconfigure(1, weight=1)

        # Cabeçalho da Tabela
        self._create_table_header(listing_frame)

        # Conteúdo da Lista (Scrollable)
        self.list_frame = ctk.CTkScrollableFrame(listing_frame)
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Controles de Paginação
        self.pagination_frame = ctk.CTkFrame(listing_frame, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))

    def _create_table_header(self, parent_frame):
        """Cria o cabeçalho da tabela de listagem."""
        headers = self._get_headers()
        header_frame = ctk.CTkFrame(parent_frame)
        header_frame.grid(row=0, column=0, sticky="ew")

        for i, header in enumerate(headers):
            header_frame.grid_columnconfigure(i, weight=1)
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")

    # --- Métodos de Paginação ---
    def _update_pagination(self):
        """Calcula o número total de páginas."""
        total_items = len(self.filtered_items)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        if self.current_page > self.total_pages:
            self.current_page = 1
        self._update_pagination_controls()

    def _update_pagination_controls(self):
        """Desenha os botões e labels de paginação."""
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        if self.total_pages <= 1:
            return

        info_label = ctk.CTkLabel(self.pagination_frame, text=f"Página {self.current_page} de {self.total_pages}")
        info_label.pack(side="left", padx=10)

        nav_frame = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        buttons = {
            "⏮️": lambda: self._go_to_page(1),
            "◀️": lambda: self._go_to_page(self.current_page - 1),
            "▶️": lambda: self._go_to_page(self.current_page + 1),
            "⏭️": lambda: self._go_to_page(self.total_pages)
        }

        for text, command in buttons.items():
            is_disabled = (("◀️" in text and self.current_page == 1) or
                           ("▶️" in text and self.current_page == self.total_pages))
            btn = ctk.CTkButton(nav_frame, text=text, command=command, width=30, state="disabled" if is_disabled else "normal")
            btn.pack(side="left", padx=2)

    def _go_to_page(self, page_number):
        """Navega para uma página específica."""
        if 1 <= page_number <= self.total_pages:
            self.current_page = page_number
            self._display_items()

    # --- Métodos de Dados e Display ---
    def _display_items(self):
        """Limpa e exibe os itens da página atual."""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        page_items = self.filtered_items[start_index:end_index]

        if not page_items:
            no_data_label = ctk.CTkLabel(self.list_frame, text="Nenhum item encontrado.")
            no_data_label.grid(row=0, column=0, pady=20)
            return

        for i, item in enumerate(page_items):
            self._create_item_row(self.list_frame, i, item)

        self._update_pagination()

    def _on_search_change(self, event=None):
        """Aplica o filtro de busca quando o texto muda."""
        query = self.search_entry.get().lower()
        if not query:
            self.filtered_items = self.items[:]
        else:
            self.filtered_items = self._perform_search(self.items, query)
        
        self.current_page = 1
        self._display_items()

    def refresh_data(self):
        """Força o recarregamento dos dados e a atualização da tela."""
        self._load_data()

    # --- Métodos Abstratos (a serem implementados pelas subclasses) ---
    def _get_headers(self):
        """Deve retornar uma lista de strings para o cabeçalho."""
        raise NotImplementedError

    def _create_item_row(self, parent, index, item):
        """Deve criar os widgets para uma linha da lista."""
        raise NotImplementedError

    def _load_data(self):
        """Deve carregar os dados em self.items e self.filtered_items."""
        raise NotImplementedError

    def _create_action_buttons(self):
        """Deve criar os botões de ação específicos da tela."""
        pass  # Opcional

    def _perform_search(self, items, query):
        """Deve implementar a lógica de busca específica."""
        # Implementação padrão (busca em todos os valores do dicionário)
        results = []
        for item in items:
            for value in item.values():
                if query in str(value).lower():
                    results.append(item)
                    break
        return results

    def on_show(self):
        """Callback quando a tela é mostrada."""
        self.refresh_data()
