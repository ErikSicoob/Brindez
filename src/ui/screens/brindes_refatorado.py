"""
Tela de Gestão de Brindes (Refatorada)
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from .base_listing_screen import BaseListingScreen
from .cadastro_brindes import CadastroBrindesScreen
from ...data.data_provider import data_provider
from tkcalendar import DateEntry

class BrindesRefatoradoScreen(BaseListingScreen):
    """Tela de gestão de brindes, herdando de BaseListingScreen."""

    def __init__(self, parent, user_manager):
        super().__init__(parent, user_manager, "Brindes")
        self.start_date_entry = None
        self.end_date_entry = None
        self.sort_combo = None
        self.cadastro_window = None
        self.setup_ui()

    # --- Métodos de UI ---

    def _create_controls_section(self):
        """Cria a seção de controles com filtros e ordenação."""
        super()._create_controls_section()

        filters_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        filters_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(5,0))

        ctk.CTkLabel(filters_frame, text="Data Início:").pack(side="left", padx=(0, 5))
        self.start_date_entry = DateEntry(filters_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.set_date(None)

        ctk.CTkLabel(filters_frame, text="Data Fim:").pack(side="left", padx=(10, 5))
        self.end_date_entry = DateEntry(filters_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.set_date(None)

        ctk.CTkLabel(filters_frame, text="Ordenar por:").pack(side="left", padx=(20, 5))
        self.sort_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Descrição", "+ Quantidade", "- Quantidade", "+ Valor Unit.", "- Valor Unit.", "+ Valor Total", "- Valor Total"],
            command=self._apply_filters_and_sort
        )
        self.sort_combo.set("Descrição")
        self.sort_combo.pack(side="left", padx=5)

        ctk.CTkButton(filters_frame, text="🔍 Aplicar", command=self._apply_filters_and_sort).pack(side="left", padx=10)
        ctk.CTkButton(filters_frame, text="🧹 Limpar", command=self._clear_filters).pack(side="left", padx=5)

    # --- Implementação dos Métodos Abstratos ---

    def _get_headers(self):
        return ["Código", "Descrição", "Categoria", "Qtde", "Valor Unit.", "Valor Total", "Ações"]

    def _load_data(self):
        try:
            self.items = data_provider.get_brindes()
        except Exception as e:
            self.items = []
            messagebox.showerror("Erro", f"Erro ao carregar brindes: {e}")
        finally:
            self._on_search_change()

    def _create_action_buttons(self):
        ctk.CTkButton(self.actions_frame, text="➕ Adicionar Brinde", command=self._add_item).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="🔄 Atualizar", command=self.refresh_data).pack(side="left", padx=5)

    def _create_item_row(self, parent, index, item):
        row_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20") if index % 2 == 0 else ("white", "gray15"))
        row_frame.pack(fill="x", expand=True, pady=1, padx=5)

        weights = [0, 3, 1, 0, 1, 1, 1]
        for i, weight in enumerate(weights):
            row_frame.grid_columnconfigure(i, weight=weight)

        valor_unit = float(item.get('valor_unitario', 0) or 0)
        quantidade = int(item.get('quantidade', 0) or 0)
        valor_total = valor_unit * quantidade

        ctk.CTkLabel(row_frame, text=item.get('codigo', 'N/A')).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('descricao', 'N/A')).grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('categoria', 'N/A')).grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=quantidade).grid(row=0, column=3, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=f"R$ {valor_unit:,.2f}").grid(row=0, column=4, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=f"R$ {valor_total:,.2f}").grid(row=0, column=5, sticky="w", padx=10)

        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=6, sticky="e", padx=5)
        ctk.CTkButton(actions_frame, text="✏️", width=30, command=lambda i=item: self._edit_item(i)).pack(side="left")
        ctk.CTkButton(actions_frame, text="🗑️", width=30, fg_color="#cc3333", command=lambda i=item: self._delete_item(i)).pack(side="left", padx=2)

    def _perform_search(self, items, query):
        filtered = super()._perform_search(items, query)

        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()
        except (tk.TclError, ValueError):
            start_date, end_date = None, None

        if start_date and end_date and start_date > end_date:
            messagebox.showwarning("Aviso", "A data de início não pode ser posterior à data de fim.")
            return filtered

        date_filtered = []
        for item in filtered:
            item_date_str = item.get('data_cadastro')
            if not item_date_str: continue
            try:
                item_date = datetime.strptime(item_date_str, '%Y-%m-%d %H:%M:%S').date()
                if (not start_date or item_date >= start_date) and (not end_date or item_date <= end_date):
                    date_filtered.append(item)
            except (ValueError, TypeError):
                continue
        filtered = date_filtered
        
        sort_key = self.sort_combo.get()
        reverse = "+" in sort_key
        
        if "Quantidade" in sort_key:
            filtered.sort(key=lambda i: int(i.get('quantidade', 0) or 0), reverse=reverse)
        elif "Valor Unit." in sort_key:
            filtered.sort(key=lambda i: float(i.get('valor_unitario', 0) or 0), reverse=reverse)
        elif "Valor Total" in sort_key:
            filtered.sort(key=lambda i: float(i.get('valor_unitario', 0) or 0) * int(i.get('quantidade', 0) or 0), reverse=reverse)
        else: # Descrição
            filtered.sort(key=lambda i: i.get('descricao', '').lower())

        return filtered

    # --- Métodos de Ação ---
    def _apply_filters_and_sort(self, event=None):
        self._on_search_change()

    def _clear_filters(self):
        self.search_entry.delete(0, 'end')
        self.start_date_entry.set_date(None)
        self.end_date_entry.set_date(None)
        self.sort_combo.set("Descrição")
        self._on_search_change()

    def _add_item(self):
        self._open_cadastro_screen()

    def _edit_item(self, item):
        self._open_cadastro_screen(brinde_data=item)

    def _delete_item(self, item):
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o brinde '{item.get('descricao')}'?", icon="warning"):
            try:
                if data_provider.delete_brinde(item['id']):
                    messagebox.showinfo("Sucesso", "Brinde excluído com sucesso.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o brinde.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir: {e}")

    def _open_cadastro_screen(self, brinde_data=None):
        if self.cadastro_window and self.cadastro_window.winfo_exists():
            self.cadastro_window.lift()
            return

        self.cadastro_window = ctk.CTkToplevel(self.frame)
        self.cadastro_window.title("Cadastro de Brinde")
        self.cadastro_window.transient(self.frame)
        self.cadastro_window.grab_set()

        def on_success_callback():
            self.refresh_data()
            if self.cadastro_window:
                self.cadastro_window.destroy()
                self.cadastro_window = None

        cadastro_frame = CadastroBrindesScreen(self.cadastro_window, self.user_manager, on_success=on_success_callback)
        # Se for edição, precisamos passar os dados
        # cadastro_frame.load_data(brinde_data) # Supondo que a tela de cadastro tenha um método para isso
        cadastro_frame.pack(fill="both", expand=True)

        def on_close():
            if self.cadastro_window:
                self.cadastro_window.destroy()
                self.cadastro_window = None

        self.cadastro_window.protocol("WM_DELETE_WINDOW", on_close)
