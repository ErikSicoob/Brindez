"""
Tela de Relatórios
"""

import customtkinter as ctk
from .base_screen import BaseScreen

class RelatoriosScreen(BaseScreen):
    """Tela de relatórios"""
    
    def __init__(self, parent):
        """Inicializa a tela de relatórios"""
        super().__init__(parent, "Relatórios")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface de relatórios"""
        # Título da tela
        self.create_title("📈 Relatórios", "Geração e visualização de relatórios")
        
        # Seção de tipos de relatórios
        self.create_report_types_section()
        
        # Seção de relatórios recentes
        self.create_recent_reports_section()
    
    def create_report_types_section(self):
        """Cria a seção de tipos de relatórios"""
        section_frame, content_frame = self.create_section("📊 Tipos de Relatórios")
        
        # Grid para os cards de relatórios
        reports_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        reports_frame.pack(fill="x")
        reports_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Relatórios disponíveis
        reports = [
            {
                "title": "📦 Estoque Atual",
                "description": "Relatório completo do estoque atual por filial",
                "icon": "📦",
                "action": self.generate_stock_report
            },
            {
                "title": "📈 Movimentações",
                "description": "Histórico de movimentações por período",
                "icon": "📈",
                "action": self.generate_movements_report
            },
            {
                "title": "🔄 Transferências",
                "description": "Relatório de transferências entre filiais",
                "icon": "🔄",
                "action": self.generate_transfers_report
            },
            {
                "title": "⚠️ Estoque Baixo",
                "description": "Itens que precisam de reposição",
                "icon": "⚠️",
                "action": self.generate_low_stock_report
            },
            {
                "title": "💰 Valor de Estoque",
                "description": "Valor financeiro do estoque por categoria",
                "icon": "💰",
                "action": self.generate_value_report
            },
            {
                "title": "👥 Usuários",
                "description": "Relatório de usuários ativos/inativos",
                "icon": "👥",
                "action": self.generate_users_report
            }
        ]
        
        # Criar cards de relatórios
        for i, report in enumerate(reports):
            row = i // 3
            col = i % 3
            
            card = ctk.CTkFrame(reports_frame)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Ícone
            icon_label = ctk.CTkLabel(
                card,
                text=report["icon"],
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(pady=(15, 5))
            
            # Título
            title_label = ctk.CTkLabel(
                card,
                text=report["title"],
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title_label.pack(pady=5)
            
            # Descrição
            desc_label = ctk.CTkLabel(
                card,
                text=report["description"],
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray50"),
                wraplength=200
            )
            desc_label.pack(pady=(0, 10), padx=10)
            
            # Botão gerar
            generate_btn = ctk.CTkButton(
                card,
                text="📄 Gerar Relatório",
                command=report["action"],
                height=35
            )
            generate_btn.pack(pady=(0, 15), padx=15, fill="x")
    
    def create_recent_reports_section(self):
        """Cria a seção de relatórios recentes"""
        section_frame, content_frame = self.create_section("📋 Relatórios Recentes")
        
        # Frame da tabela
        table_frame = ctk.CTkFrame(content_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Cabeçalho da tabela
        header_frame = ctk.CTkFrame(table_frame, fg_color=("gray80", "gray30"))
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        headers = ["Data/Hora", "Tipo", "Usuário", "Status", "Ações"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # Dados mock
        mock_data = [
            ("22/09/2025 10:15", "Estoque Atual", "Admin", "Concluído", "stock_001"),
            ("21/09/2025 16:30", "Movimentações", "João Silva", "Concluído", "mov_002"),
            ("21/09/2025 14:45", "Estoque Baixo", "Maria Santos", "Concluído", "low_003"),
            ("20/09/2025 09:20", "Transferências", "Admin", "Concluído", "trans_004"),
            ("19/09/2025 11:10", "Valor Estoque", "Pedro Costa", "Concluído", "value_005")
        ]
        
        # Linhas da tabela
        for i, (data, tipo, user, status, report_id) in enumerate(mock_data):
            row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=2)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            # Células
            cells = [data, tipo, user, status]
            for j, cell in enumerate(cells):
                color = "green" if cell == "Concluído" else None
                label = ctk.CTkLabel(row_frame, text=cell, text_color=color)
                label.grid(row=0, column=j, padx=10, pady=5, sticky="ew")
            
            # Botões de ação
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=4, padx=10, pady=5, sticky="ew")
            
            download_btn = ctk.CTkButton(
                actions_frame, 
                text="📥", 
                width=30, 
                height=25, 
                command=lambda r=report_id: self.download_report(r)
            )
            download_btn.pack(side="left", padx=2)
            
            view_btn = ctk.CTkButton(
                actions_frame, 
                text="👁️", 
                width=30, 
                height=25, 
                command=lambda r=report_id: self.view_report(r)
            )
            view_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame, 
                text="🗑️", 
                width=30, 
                height=25, 
                command=lambda r=report_id: self.delete_report(r)
            )
            delete_btn.pack(side="left", padx=2)
    
    def generate_stock_report(self):
        """Gera relatório de estoque atual"""
        print("Gerar relatório de estoque - TODO: Implementar")
    
    def generate_movements_report(self):
        """Gera relatório de movimentações"""
        print("Gerar relatório de movimentações - TODO: Implementar")
    
    def generate_transfers_report(self):
        """Gera relatório de transferências"""
        print("Gerar relatório de transferências - TODO: Implementar")
    
    def generate_low_stock_report(self):
        """Gera relatório de estoque baixo"""
        print("Gerar relatório de estoque baixo - TODO: Implementar")
    
    def generate_value_report(self):
        """Gera relatório de valor de estoque"""
        print("Gerar relatório de valor - TODO: Implementar")
    
    def generate_users_report(self):
        """Gera relatório de usuários"""
        print("Gerar relatório de usuários - TODO: Implementar")
    
    def download_report(self, report_id):
        """Baixa um relatório"""
        print(f"Baixar relatório {report_id} - TODO: Implementar")
    
    def view_report(self, report_id):
        """Visualiza um relatório"""
        print(f"Visualizar relatório {report_id} - TODO: Implementar")
    
    def delete_report(self, report_id):
        """Exclui um relatório"""
        print(f"Excluir relatório {report_id} - TODO: Implementar")
