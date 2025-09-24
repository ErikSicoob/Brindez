"""
Tela de Movimentações de Estoque
"""

import customtkinter as ctk
from .base_screen import BaseScreen
from ...data.data_provider import data_provider
from datetime import datetime

class MovimentacoesScreen(BaseScreen):
    """Tela de movimentações de estoque"""
    
    def __init__(self, parent):
        """Inicializa a tela de movimentações"""
        super().__init__(parent, "Movimentações")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface de movimentações"""
        # Título da tela
        self.create_title("📦 Movimentações de Estoque", "Histórico e controle de movimentações")
        
        # Seção de filtros
        self.create_filters_section()
        
        # Seção de histórico
        self.create_history_section()
    
    def create_filters_section(self):
        """Cria a seção de filtros"""
        section_frame, content_frame = self.create_section("🔍 Filtros")
        
        # Frame para filtros
        filters_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        filters_frame.pack(fill="x")
        filters_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Filtro por tipo
        type_label = ctk.CTkLabel(filters_frame, text="📋 Tipo:")
        type_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.type_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos", "Entrada", "Saída", "Transferência"]
        )
        self.type_combo.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por período
        period_label = ctk.CTkLabel(filters_frame, text="📅 Período:")
        period_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.period_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Hoje", "Esta Semana", "Este Mês", "Últimos 3 Meses", "Personalizado"]
        )
        self.period_combo.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        
        # Filtro por usuário
        user_label = ctk.CTkLabel(filters_frame, text="👤 Usuário:")
        user_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.user_combo = ctk.CTkComboBox(
            filters_frame,
            values=["Todos", "Admin", "João Silva", "Maria Santos", "Pedro Costa"]
        )
        self.user_combo.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        # Filtro por filial
        filial_label = ctk.CTkLabel(filters_frame, text="🏢 Filial:")
        filial_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        try:
            filiais = data_provider.get_filiais() or []
            filial_values = ["Todas"] + [f.get('nome', 'N/A') for f in filiais]
        except Exception:
            filial_values = ["Todas"]
        self.filial_combo = ctk.CTkComboBox(
            filters_frame,
            values=filial_values
        )
        self.filial_combo.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")

        # Restringir seleção de filial para usuários não-Admin e não-globais ('00')
        try:
            user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
            if user and getattr(self.user_manager, 'is_admin', lambda: False)() is False:
                user_filial = user.get('filial')
                # Verificar se a filial do usuário é global (numero '00')
                is_global = False
                try:
                    filiais_all = data_provider.get_filiais() or []
                    fil = next((f for f in filiais_all if f.get('nome') == user_filial), None)
                    if fil and str(fil.get('numero')).zfill(2) == '00':
                        is_global = True
                except Exception:
                    is_global = (user_filial == 'Matriz')
                if not is_global:
                    self.filial_combo.configure(values=[user_filial])
                    self.filial_combo.set(user_filial)
                    self.filial_combo.configure(state="disabled")
                else:
                    # Padrão para global/Admin
                    self.filial_combo.set("Todas")
        except Exception:
            pass
        
        # Botão filtrar
        filter_button = ctk.CTkButton(
            filters_frame,
            text="🔍 Filtrar",
            command=self.apply_filters,
            height=40
        )
        filter_button.grid(row=1, column=3, padx=10, pady=(0, 10), sticky="ew")
    
    def create_history_section(self):
        """Cria a seção de histórico"""
        section_frame, content_frame = self.create_section("📋 Histórico de Movimentações")
        
        # Frame da tabela
        table_frame = ctk.CTkFrame(content_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        headers = ["Data/Hora", "Tipo", "Item", "Quantidade", "Usuário", "Justificativa", "Detalhes"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=5, pady=10, sticky="ew")
        
        # Obter movimentações reais e aplicar filtro de filial
        movimentacoes = data_provider.get_movimentacoes(limit=50) or []
        try:
            selected_filial = self.filial_combo.get() if hasattr(self, 'filial_combo') else "Todas"
        except Exception:
            selected_filial = "Todas"
        # Forçar restrição por perfil (considerando filial global '00')
        try:
            user = self.user_manager.get_current_user() if hasattr(self, 'user_manager') else None
            if user and getattr(self.user_manager, 'is_admin', lambda: False)() is False:
                user_filial = user.get('filial')
                is_global = False
                try:
                    filiais_all = data_provider.get_filiais() or []
                    fil = next((f for f in filiais_all if f.get('nome') == user_filial), None)
                    if fil and str(fil.get('numero')).zfill(2) == '00':
                        is_global = True
                except Exception:
                    is_global = (user_filial == 'Matriz')
                if not is_global:
                    selected_filial = user_filial
        except Exception:
            pass

        if selected_filial and selected_filial != "Todas":
            movimentacoes = [m for m in movimentacoes if m.get('filial') == selected_filial]
        
        # Linhas da tabela
        for i, mov in enumerate(movimentacoes):
            # Formatar data
            data_hora = mov.get('data_hora', '')
            if data_hora:
                try:
                    dt = datetime.fromisoformat(data_hora)
                    data_formatada = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    data_formatada = data_hora
            else:
                data_formatada = "N/A"
            
            # Dados da movimentação
            tipo = mov.get('tipo', '').title()
            item = mov.get('brinde_descricao', 'N/A')
            quantidade = mov.get('quantidade', 0)
            qty_str = f"+{quantidade}" if tipo == "Entrada" else f"-{quantidade}"
            user = mov.get('usuario', 'N/A')
            # Coagir campos potencialmente None para strings seguras
            justificativa_raw = mov.get('justificativa')
            observacoes_raw = mov.get('observacoes')
            destino_raw = mov.get('destino')

            justificativa = str(justificativa_raw if justificativa_raw not in (None, '') else (observacoes_raw if observacoes_raw not in (None, '') else 'N/A'))
            detalhes = str(destino_raw if destino_raw not in (None, '') else (observacoes_raw if observacoes_raw not in (None, '') else 'N/A'))
            
            data = data_formatada
            just = justificativa[:50] + "..." if len(justificativa) > 50 else justificativa
            det = detalhes[:50] + "..." if len(detalhes) > 50 else detalhes
            row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
            
            # Cor baseada no tipo
            if "Entrada" in tipo:
                color = "green"
            elif "Saída" in tipo:
                color = "red"
            else:  # Transferência
                color = "blue"
            
            # Células
            cells = [data, tipo, item, qty_str, user, just, det]
            for j, cell in enumerate(cells):
                text_color = color if j == 1 or j == 3 else None  # Tipo e Quantidade coloridos
                label = ctk.CTkLabel(
                    row_frame, 
                    text=cell, 
                    text_color=text_color,
                    font=ctk.CTkFont(size=10)
                )
                label.grid(row=0, column=j, padx=5, pady=5, sticky="ew")
        
        # Paginação
        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=10, pady=10)
        
        # Informações da página
        page_info = ctk.CTkLabel(
            pagination_frame,
            text="Mostrando 6 de 156 registros - Página 1 de 26",
            font=ctk.CTkFont(size=11)
        )
        page_info.pack(side="left")
        
        # Botões de navegação
        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right")
        
        prev_btn = ctk.CTkButton(nav_frame, text="◀ Anterior", width=80, height=30, command=self.prev_page)
        prev_btn.pack(side="left", padx=5)
        
        next_btn = ctk.CTkButton(nav_frame, text="Próxima ▶", width=80, height=30, command=self.next_page)
        next_btn.pack(side="left", padx=5)
    
    def apply_filters(self):
        """Aplica os filtros selecionados"""
        print("Aplicar filtros - TODO: Implementar")
    
    def prev_page(self):
        """Página anterior"""
        print("Página anterior - TODO: Implementar")
    
    def next_page(self):
        """Próxima página"""
        print("Próxima página - TODO: Implementar")
