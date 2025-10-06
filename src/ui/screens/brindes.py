"""
Tela de Gestão de Brindes
"""

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from .base_screen import BaseScreen
from ..components.form_dialog import FormDialog
from .cadastro_brindes import CadastroBrindesScreen
from ...data.data_provider import data_provider
from ...utils.validators import BrindeValidator, MovimentacaoValidator, ValidationError, BusinessRuleError

from .base_listing_screen import BaseListingScreen
from collections import defaultdict

class BrindesScreen(BaseListingScreen):
    """Tela de gestão de brindes (Refatorada), herdando de BaseListingScreen."""
    
    def __init__(self, parent, user_manager):
        super().__init__(parent, user_manager, "Brindes")
        self._aggregated_code_map = {}
        self.items_per_page = 20 # Brindes podem ter mais itens
        self.setup_ui()

    # --- Implementação dos Métodos Abstratos ---

    def _get_headers(self):
        """Retorna os cabeçalhos da tabela de brindes."""
        return ["Código", "Descrição", "Categoria", "Quantidade", "Valor Unit.", "Valor Total", "Ações"]

    def _load_data(self):
        """Carrega e pré-processa os dados dos brindes."""
        try:
            self.items = data_provider.get_brindes()
            # A filtragem e consolidação ocorrerão no _perform_search
            self._on_search_change() # Força a aplicação inicial dos filtros
        except Exception as e:
            self.items = []
            self.filtered_items = []
            messagebox.showerror("Erro", f"Erro ao carregar brindes: {e}")
            self._display_items()
        
    # --- Sobrescrita dos Métodos de UI ---

    def _create_controls_section(self):
        """Cria a seção de controles com filtros adicionais para brindes."""
        # Chama o método da classe base primeiro para criar o controls_frame
        super()._create_controls_section()
        
        # Cria um novo frame para os filtros específicos de brindes
        filters_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        filters_frame.grid(row=0, column=1, sticky="e", padx=10)
        
        # Configura o grid do controls_frame para acomodar os filtros
        self.controls_frame.grid_columnconfigure(1, weight=1)
        
        try:
            # Filtro de Categoria
            ctk.CTkLabel(filters_frame, text="Categoria:").pack(side="left", padx=(0, 5))
            self.category_combo = ctk.CTkComboBox(
                filters_frame, 
                values=["Todas"] + data_provider.get_categorias(),
                command=lambda _: self._on_search_change()
            )
            self.category_combo.set("Todas")
            self.category_combo.pack(side="left", padx=5)

            # Filtro de Filial
            ctk.CTkLabel(filters_frame, text="Filial:").pack(side="left", padx=(10, 5))
            self.filial_combo = ctk.CTkComboBox(
                filters_frame, 
                values=["Todas"] + [f['nome'] for f in data_provider.get_filiais()],
                command=lambda _: self._on_search_change()
            )
            self.filial_combo.set("Todas")
            self.filial_combo.pack(side="left", padx=5)
            
        except Exception as e:
            print(f"Erro ao carregar filtros: {e}")
            # Se houver erro, continua sem os filtros adicionais

    def _create_action_buttons(self):
        """Cria os botões de ação específicos para brindes."""
        ctk.CTkButton(self.actions_frame, text="➕ Novo Brinde", command=self._new_item).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="🔄 Atualizar", command=self.refresh_data).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="📥 Importar", command=self._import_items).pack(side="left", padx=5)
        ctk.CTkButton(self.actions_frame, text="📤 Exportar", command=self._export_items).pack(side="left", padx=5)
    
    # --- Lógica de Busca e Filtragem (Sobrescrita) ---

    def _perform_search(self, items, query):
        """Aplica filtros de busca, categoria, filial e consolida os resultados."""
        # 1. Filtros básicos
        search_text = query.lower()
        category = self.category_combo.get()
        filial = self.filial_combo.get()

        filtered = items
        if search_text:
            filtered = [i for i in filtered if search_text in str(i.get('codigo', '')).lower() or search_text in str(i.get('descricao', '')).lower()]
        if category != "Todas":
            filtered = [i for i in filtered if i.get('categoria') == category]
        if filial != "Todas":
            filtered = [i for i in filtered if i.get('filial') == filial]

        # 2. Consolidação por descrição
        totals_by_desc = defaultdict(lambda: {'quantidade': 0, 'valor_total': 0, 'rep': None})
        for item in filtered:
            desc_key = str(item.get('descricao', '')).strip().lower()
            if not desc_key: continue
            
            totals_by_desc[desc_key]['quantidade'] += int(item.get('quantidade', 0) or 0)
            totals_by_desc[desc_key]['valor_total'] += float(item.get('valor_total', 0) or 0)
            if not totals_by_desc[desc_key]['rep']:
                totals_by_desc[desc_key]['rep'] = item

        # 3. Montar a lista final para exibição
        display_list = []
        self._aggregated_code_map.clear()
        for desc_key, data in totals_by_desc.items():
            rep = data['rep']
            display_list.append({
                'id': rep.get('id'),
                'codigo': rep.get('codigo'),
                'descricao': rep.get('descricao'),
                'categoria': rep.get('categoria'),
                'valor_unitario': rep.get('valor_unitario', 0),
                'quantidade': data['quantidade'],
                'valor_total': data['valor_total']
            })
            self._aggregated_code_map[desc_key] = rep.get('codigo')
        
        return display_list

    # --- Lógica de Renderização e Ações ---

    def _create_item_row(self, parent, index, item):
        """Cria a representação visual de uma linha de brinde consolidado."""
        row_frame = ctk.CTkFrame(parent, fg_color=("gray90", "gray20") if index % 2 == 0 else ("white", "gray15"))
        row_frame.pack(fill="x", expand=True, pady=1, padx=5)

        columns = self._get_headers()
        for i in range(len(columns)):
            row_frame.grid_columnconfigure(i, weight=1)

        # Formatação de valores
        valor_unit = float(item.get('valor_unitario', 0))
        valor_total = float(item.get('valor_total', 0))

        # Dados da linha
        ctk.CTkLabel(row_frame, text=item.get('codigo', 'N/A')).grid(row=0, column=0, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('descricao', 'N/A')).grid(row=0, column=1, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('categoria', 'N/A')).grid(row=0, column=2, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=item.get('quantidade', 0)).grid(row=0, column=3, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=f"R$ {valor_unit:,.2f}").grid(row=0, column=4, sticky="w", padx=10)
        ctk.CTkLabel(row_frame, text=f"R$ {valor_total:,.2f}").grid(row=0, column=5, sticky="w", padx=10)

        # Botões de Ação
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=6, sticky="e", padx=5)
        ctk.CTkButton(actions_frame, text="✏️", width=30, command=lambda i=item: self._edit_item(i)).pack(side="left")
        ctk.CTkButton(actions_frame, text="🗑️", width=30, fg_color="#cc3333", command=lambda i=item: self._delete_item(i)).pack(side="left", padx=2)

    def _new_item(self):
        self._open_cadastro_screen()

    def _edit_item(self, item):
        # Para editar, precisamos do código original, não o consolidado
        desc_key = str(item.get('descricao', '')).strip().lower()
        original_code = self._aggregated_code_map.get(desc_key, item.get('codigo'))
        # Encontrar o brinde original para passar para a tela de edição
        original_item = next((i for i in self.items if i.get('codigo') == original_code), None)
        if original_item:
            self._open_cadastro_screen(brinde_data=original_item)
        else:
            messagebox.showwarning("Aviso", "Não foi possível encontrar o item original para edição.")

    def _delete_item(self, item):
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja excluir o brinde '{item.get('descricao')}' e todos os seus registros de estoque?", icon="warning"):
            try:
                # A exclusão deve ser feita pelo ID do item representativo
                if data_provider.delete_brinde(item['id']):
                    messagebox.showinfo("Sucesso", "Brinde excluído com sucesso.")
                    self.refresh_data()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o brinde.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    def _open_cadastro_screen(self, brinde_data=None):
        if hasattr(self, 'cadastro_window') and self.cadastro_window.winfo_exists():
            self.cadastro_window.lift()
            return

        self.cadastro_window = ctk.CTkToplevel(self.frame)
        self.cadastro_window.title("Cadastro de Brinde")
        self.cadastro_window.transient(self.frame)
        self.cadastro_window.grab_set()

        def on_success():
            self.refresh_data()
            self.cadastro_window.destroy()

        cadastro_frame = CadastroBrindesScreen(self.cadastro_window, self.user_manager, brinde_data=brinde_data, on_success=on_success)
        cadastro_frame.pack(fill="both", expand=True)
        self.cadastro_window.protocol("WM_DELETE_WINDOW", lambda: self.cadastro_window.destroy())

    # --- Métodos específicos (Importar/Exportar) ---
    def _import_items(self):
        messagebox.showinfo("Info", "Funcionalidade de importar brindes a ser implementada.")

    def _export_items(self):
        messagebox.showinfo("Info", "Funcionalidade de exportar brindes a ser implementada.")
    
    
    
    
    
    
    

    def new_brinde(self):
        """Abre o formulário modal para cadastro de novo brinde"""
        try:
            # Se a janela já existe, apenas trazer para frente
            if self.cadastro_screen is not None and hasattr(self.cadastro_screen, 'window') and self.cadastro_screen.window.winfo_exists():
                self.cadastro_screen.window.lift()
                self.cadastro_screen.window.focus_force()
                return
                
            # Obter a janela raiz
            parent_window = self._get_root()
            if not parent_window or not parent_window.winfo_exists():
                parent_window = ctk.CTk()
                parent_window.withdraw()
            
            # Criar a tela de cadastro como um modal
            self.cadastro_screen = CadastroBrindesScreen(
                parent=parent_window,
                user_manager=self.user_manager,
                on_success=self.on_brinde_created
            )
            
            # Configurar o que acontece quando o modal for fechado
            def on_modal_close():
                try:
                    if (self.cadastro_screen is not None and 
                        hasattr(self.cadastro_screen, 'window') and 
                        self.cadastro_screen.window.winfo_exists()):
                        self.cadastro_screen.window.grab_release()
                        self.cadastro_screen.window.destroy()
                except Exception as e:
                    print(f"Erro ao fechar janela: {e}")
                finally:
                    self.cadastro_screen = None
            
            # Configurar o protocolo de fechamento da janela
            if hasattr(self.cadastro_screen, 'window') and self.cadastro_screen.window.winfo_exists():
                self.cadastro_screen.window.protocol("WM_DELETE_WINDOW", on_modal_close)
                self.cadastro_screen.window.focus_force()
            
        except Exception as e:
            print(f"Erro ao abrir cadastro de brinde: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao abrir cadastro de brinde: {e}")
            # Limpar referência em caso de erro
            self.cadastro_screen = None
            # Garantir que a tela atual continue visível
            if hasattr(self, 'show'):
                self.show()
            
    def _get_root(self):
        """Obtém a janela raiz da aplicação"""
        # Tenta obter o widget raiz de várias maneiras
        widget = self
        
        # Primeiro tenta encontrar o widget raiz através de parent
        if hasattr(self, 'parent') and self.parent is not None:
            widget = self.parent
            while hasattr(widget, 'parent') and widget.parent is not None:
                widget = widget.parent
        # Se não encontrar, tenta através de master
        elif hasattr(self, 'master') and self.master is not None:
            widget = self.master
            while hasattr(widget, 'master') and widget.master is not None:
                widget = widget.master
        # Se ainda não encontrou, tenta obter a janela atual
        elif hasattr(self, 'winfo_toplevel'):
            return self.winfo_toplevel()
            
        # Se o widget atual não for uma janela, sobe na hierarquia
        while hasattr(widget, 'winfo_parent') and widget.winfo_parent():
            widget = widget._nametowidget(widget.winfo_parent())
            
        return widget
    
    def on_brinde_created(self):
        """Callback chamado quando um brinde é criado com sucesso"""
        try:
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", "Brinde cadastrado com sucesso!")
            
            # Fechar a janela de cadastro se existir
            if (self.cadastro_screen is not None and 
                hasattr(self.cadastro_screen, 'window') and 
                self.cadastro_screen.window.winfo_exists()):
                self.cadastro_screen.window.destroy()
            
            # Recarregar dados
            self._load_initial_data()
            self.refresh_table()
            
            # Garantir que a tela está visível
            if hasattr(self, 'show'):
                self.show()
            
        except Exception as e:
            print(f"Erro ao atualizar lista de brindes: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao atualizar lista de brindes: {e}")
        finally:
            # Limpar a referência à janela de cadastro
            self.cadastro_screen = None
    
    def _safe_get_fornecedor_names(self):
        """Obtém nomes de fornecedores de forma segura"""
        try:
            fornecedores = data_provider.get_fornecedores()
            if isinstance(fornecedores, list):
                return [f.get('nome', 'N/A') for f in fornecedores if f and f.get('nome')]
            else:
                print(f"Erro: get_fornecedores() retornou {type(fornecedores)} ao invés de list")
                return []
        except Exception as e:
            print(f"Erro ao obter fornecedores: {e}")
            return []
    
    def save_new_brinde(self, data):
        """Salva um novo brinde"""
        try:
            # Validar dados usando o validador específico
            validated_data = BrindeValidator.validate_brinde_data(
                data,
                data_provider.get_categorias(),
                data_provider.get_unidades_medida(),
                [f.get('nome', 'N/A') for f in data_provider.get_filiais() if f.get('nome')]
            )

            # Adicionar usuário atual
            user = self.user_manager.get_current_user()
            if user:
                validated_data['usuario_cadastro'] = user.get('username', 'admin')

            # Nova lógica: alocação manual por filial com quantidades
            # Campo 'filial' vem como dict {nome_filial: quantidade}
            alocacoes = validated_data.pop('filial', {}) or {}
            quantidade_total = int(validated_data.get('quantidade', 0))

            if not isinstance(alocacoes, dict) or not alocacoes:
                raise ValidationError("Selecione pelo menos uma filial e informe a quantidade para cada uma.")

            soma_alocada = sum(int(v or 0) for v in alocacoes.values())
            if soma_alocada != quantidade_total:
                raise ValidationError(
                    f"A soma das quantidades por filial ({soma_alocada}) deve ser igual à quantidade total digitada ({quantidade_total})."
                )

            # Criar um registro por filial com a quantidade alocada
            for filial, qtd in alocacoes.items():
                qtd_int = int(qtd or 0)
                if qtd_int < 0:
                    raise ValidationError("Quantidade por filial não pode ser negativa.")
                if qtd_int == 0:
                    continue  # ignorar alocação zero
                brinde_data = validated_data.copy()
                brinde_data['filial'] = filial
                brinde_data['quantidade'] = qtd_int
                data_provider.create_brinde(brinde_data)

            # Atualização imediata e otimizada
            self.refresh_brindes_list()

            messagebox.showinfo("Sucesso", "Brinde(s) cadastrado(s) com sucesso!")
            return True

        except ValidationError as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except BusinessRuleError as e:
            messagebox.showerror("Erro de Regra de Negócio", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar brinde: {e.__class__.__name__}: {e}")
            return False
    
    def save_edit_brinde(self, brinde_id, data):
        """Salva edição de um brinde"""
        try:
            # Validar dados usando o validador específico
            validated_data = BrindeValidator.validate_brinde_data(
                data,
                data_provider.get_categorias(),
                data_provider.get_unidades_medida(),
                [f.get('nome', 'N/A') for f in data_provider.get_filiais() if f.get('nome')]
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
        todas_as_filiais = [f.get('nome', 'N/A') for f in data_provider.get_filiais() if f.get('nome')]
        
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
            todas_filiais = data_provider.get_filiais() or []
        except Exception:
            todas_filiais = []
        accessible_filiais = [f.get('nome') for f in todas_filiais] or [brinde.get('filial')]
        try:
            if self.user_manager and not self.user_manager.is_admin() and user_filial:
                # Checar se usuário é global (numero '00')
                is_global = False
                try:
                    fil = next((f for f in todas_filiais if f.get('nome') == user_filial), None)
                    if fil and str(fil.get('numero')).zfill(2) == '00':
                        is_global = True
                except Exception:
                    is_global = (user_filial == 'Matriz')
                if not is_global:
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
            # Confirmar exclusão
            if messagebox.askyesno("Confirmar Exclusão", f"Excluir '{descricao}'?"):
                # Excluir do banco
                if data_provider.delete_brinde(brinde_id):
                    # Remover da lista atual imediatamente (antes do refresh) para UX consistente
                    try:
                        self.current_brindes = [b for b in self.current_brindes if b.get('id') != brinde_id]
                        self.apply_filters()
                        self.refresh_table()
                    except Exception:
                        pass
                    # Atualização a partir da fonte de dados
                    self.refresh_brindes_list()
                    
                    # Mostrar mensagem de sucesso
                    messagebox.showinfo("Sucesso", f"'{descricao}' excluído com sucesso!")
                else:
                    messagebox.showerror("Erro", "Falha na exclusão")
        except Exception as e:
            print(f"ERRO delete_brinde: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro interno na exclusão: {e}")
    
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
