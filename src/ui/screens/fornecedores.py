"""
Tela de Gestão de Fornecedores (Refatorada)
"""

import customtkinter as ctk
from tkinter import messagebox
from .base_listing_screen import BaseListingScreen
from .cadastro_fornecedor import CadastroFornecedorScreen
from ...data.data_provider import data_provider

class FornecedoresScreen(BaseListingScreen):
    """Tela de gestão de fornecedores, herdando de BaseListingScreen."""

    def __init__(self, parent, user_manager):
        super().__init__(parent, user_manager, "Fornecedores")
        self.setup_ui()

    # --- Implementação dos Métodos Abstratos ---

    def _get_headers(self):
        """Retorna os cabeçalhos da tabela de fornecedores."""
        return ["Código", "Nome", "Contato", "Telefone", "Ações"]

    def _load_data(self):
        """Carrega os dados dos fornecedores."""
        try:
            self.items = data_provider.get_fornecedores()
            self.filtered_items = self.items[:]
            self._display_items()
        except Exception as e:
            self.items = []
            self.filtered_items = []
            messagebox.showerror("Erro", f"Erro ao carregar fornecedores: {e}")
            self._display_items() # Exibe a mensagem de 'nenhum item'

    def _create_action_buttons(self):
        """Cria os botões de 'Novo' e 'Atualizar'."""
        new_button = ctk.CTkButton(self.actions_frame, text="➕ Novo Fornecedor", command=self._new_item)
        new_button.pack(side="left", padx=5)

        refresh_button = ctk.CTkButton(self.actions_frame, text="🔄 Atualizar", command=self.refresh_data)
        refresh_button.pack(side="left", padx=5)

    def _create_item_row(self, parent, index, item):
        """Cria a representação visual de uma linha de fornecedor."""
        row_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20") if index % 2 == 0 else ("white", "gray15"))
        row_frame.pack(fill="x", expand=True, pady=1, padx=5)

        columns = self._get_headers()
        for i in range(len(columns)):
            row_frame.grid_columnconfigure(i, weight=1)

        # Dados da linha
        ctk.CTkLabel(row_frame, text=item.get('codigo', 'N/A')).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('nome', 'N/A')).grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('contato_nome', 'N/A')).grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('telefone', 'N/A')).grid(row=0, column=3, sticky="w", padx=10)

        # Botões de Ação na Linha
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=4, sticky="e", padx=5)

        edit_button = ctk.CTkButton(actions_frame, text="✏️", width=30, command=lambda i=item: self._edit_item(i))
        edit_button.pack(side="left", padx=2)

        delete_button = ctk.CTkButton(actions_frame, text="🗑️", width=30, fg_color="#cc3333", command=lambda i=item: self._delete_item(i))
        delete_button.pack(side="left", padx=2)

    # --- Lógica Específica de Fornecedores ---

    def _new_item(self):
        """Abre a tela de cadastro para um novo fornecedor."""
        self._open_cadastro_screen()

    def _edit_item(self, item):
        """Abre a tela de cadastro para editar um fornecedor existente."""
        self._open_cadastro_screen(fornecedor_data=item)

    def _delete_item(self, item):
        """Exclui um fornecedor após confirmação."""
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o fornecedor '{item.get('nome')}'?", icon="warning"):
            try:
                if data_provider.delete_fornecedor(item['id']):
                    messagebox.showinfo("Sucesso", "Fornecedor excluído com sucesso.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o fornecedor.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def _open_cadastro_screen(self, fornecedor_data=None):
        """Abre a tela de cadastro/edição de forma modal."""
        # Usamos um Toplevel para criar uma janela modal
        if hasattr(self, 'cadastro_window') and self.cadastro_window.winfo_exists():
            self.cadastro_window.lift()
            return

        self.cadastro_window = ctk.CTkToplevel(self.frame)
        self.cadastro_window.title("Cadastro de Fornecedor")
        self.cadastro_window.transient(self.frame)
        self.cadastro_window.grab_set()

        def on_success():
            self.refresh_data()
            self.cadastro_window.destroy()

        cadastro_frame = CadastroFornecedorScreen(self.cadastro_window, self.user_manager, fornecedor_data, on_success)
        cadastro_frame.pack(fill="both", expand=True)

        self.cadastro_window.protocol("WM_DELETE_WINDOW", lambda: self.cadastro_window.destroy())
