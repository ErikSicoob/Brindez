"""
Tela do Dashboard - Indicadores principais
"""

import customtkinter as ctk
from .base_screen import BaseScreen
from ...data.data_provider import data_provider
from ...utils.formatters import format_currency, format_relative_time
from datetime import datetime

class DashboardScreen(BaseScreen):
    """Tela do Dashboard"""
    
    def __init__(self, parent):
        """Inicializa a tela do dashboard"""
        super().__init__(parent, "Dashboard")
        self.auto_refresh_ms = 10000  # 10s
        self.setup_ui()
        self.schedule_auto_refresh()
    
    def setup_ui(self):
        """Configura a interface do dashboard"""
        # Título da tela
        self.create_title("📊 Dashboard", "Visão geral do sistema de brindes")
        
        # Cards de indicadores
        self.create_indicators_section()
        
        # Gráficos e informações adicionais
        self.create_charts_section()
        
        # Alertas e notificações
        self.create_alerts_section()
    
    def create_indicators_section(self):
        """Cria a seção de indicadores principais"""
        section_frame, content_frame = self.create_section("📈 Indicadores Principais")
        
        # Frame para os cards
        cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        cards_frame.pack(fill="x")
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Obter estatísticas do data provider
        stats = data_provider.get_estatisticas_dashboard()
        
        total_itens = stats['total_itens']
        categorias = stats['total_categorias']
        valor_total = stats['valor_total']
        itens_baixo = stats['itens_estoque_baixo']
        
        # Card 1: Total de Itens
        self.create_indicator_card(
            cards_frame, 
            "🎁 Total de Itens", 
            f"{total_itens:,}".replace(',', '.'), 
            "itens em estoque",
            row=0, column=0
        )
        
        # Card 2: Categorias
        self.create_indicator_card(
            cards_frame, 
            "📂 Categorias", 
            str(categorias), 
            "categorias ativas",
            row=0, column=1
        )
        
        # Card 3: Valor Total
        self.create_indicator_card(
            cards_frame, 
            "💰 Valor Total", 
            f"R$ {valor_total:,.2f}".replace(',', '.').replace('.', ',', 1), 
            "valor do estoque",
            row=0, column=2
        )
        
        # Card 4: Estoque Baixo
        self.create_indicator_card(
            cards_frame, 
            "⚠️ Estoque Baixo", 
            str(itens_baixo), 
            "itens precisam reposição",
            row=0, column=3,
            alert=itens_baixo > 0
        )
    
    def create_indicator_card(self, parent, title, value, description, row, column, alert=False):
        """Cria um card de indicador"""
        # Cor do card baseada no alerta
        fg_color = ("red", "darkred") if alert else ("gray90", "gray20")
        
        card = ctk.CTkFrame(parent, fg_color=fg_color)
        card.grid(row=row, column=column, padx=10, pady=10, sticky="ew")
        
        # Título
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        title_label.pack(pady=(15, 5))
        
        # Valor principal
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        value_label.pack(pady=5)
        
        # Descrição
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        desc_label.pack(pady=(0, 15))
    
    def create_charts_section(self):
        """Cria a seção de gráficos"""
        section_frame, content_frame = self.create_section("📊 Análises")
        
        # Frame para gráficos lado a lado
        charts_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        charts_frame.pack(fill="x")
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Gráfico 1: Estoque por Categoria (mock)
        chart1_frame = ctk.CTkFrame(charts_frame)
        chart1_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        chart1_title = ctk.CTkLabel(
            chart1_frame,
            text="📊 Estoque por Categoria",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        chart1_title.pack(pady=(15, 10))
        
        # Dados reais de categoria
        brindes = data_provider.get_brindes()
        total_itens = sum(b.get('quantidade', 0) for b in brindes)
        
        # Agrupar por categoria
        categorias_count = {}
        for brinde in brindes:
            categoria = brinde.get('categoria', 'Outros')
            categorias_count[categoria] = categorias_count.get(categoria, 0) + brinde.get('quantidade', 0)
        
        # Calcular percentuais e ordenar
        categories_data = []
        for categoria, quantidade in sorted(categorias_count.items(), key=lambda x: x[1], reverse=True):
            if total_itens > 0:
                percentual = (quantidade / total_itens) * 100
                categories_data.append((categoria, f"{percentual:.1f}%", quantidade))
        
        for cat, percent, qty in categories_data:
            cat_frame = ctk.CTkFrame(chart1_frame, fg_color="transparent")
            cat_frame.pack(fill="x", padx=15, pady=2)
            
            cat_label = ctk.CTkLabel(cat_frame, text=f"{cat}: {qty} itens ({percent})", anchor="w")
            cat_label.pack(side="left")
        
        # Espaçamento
        ctk.CTkLabel(chart1_frame, text="").pack(pady=10)
        
        # Gráfico 2: Movimentações Recentes (mock)
        chart2_frame = ctk.CTkFrame(charts_frame)
        chart2_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        
        chart2_title = ctk.CTkLabel(
            chart2_frame,
            text="📦 Movimentações Recentes",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        chart2_title.pack(pady=(15, 10))
        
        # Movimentações reais recentes (texto amigável)
        movimentacoes = data_provider.get_movimentacoes(limit=5)
        movements_data = []
        
        for mov in movimentacoes:
            tipo_raw = (mov.get('tipo', '') or '').lower()
            mov_type = mov.get('tipo', '').replace('_', ' ').title()
            item = mov.get('brinde_descricao', 'Item')
            quantidade = mov.get('quantidade', 0)
            filial_origem = mov.get('filial_origem') or mov.get('filial') or ''
            filial_destino = mov.get('filial_destino') or ''
            if 'entrada' in tipo_raw:
                texto = f"Entrada: {quantidade}x {item} em {filial_origem or 'filial não informada'}"
            elif 'saida' in tipo_raw:
                texto = f"Saída: {quantidade}x {item} de {filial_origem or 'filial não informada'}"
            elif 'transferencia' in tipo_raw:
                texto = f"Transferência: {quantidade}x {item} — {filial_origem or '?'} -> {filial_destino or '?'}"
            else:
                texto = f"{mov_type}: {quantidade}x {item}"
            
            # Calcular tempo relativo
            data_hora = mov.get('data_hora', '')
            if data_hora:
                try:
                    dt = datetime.fromisoformat(data_hora)
                    now = datetime.now()
                    diff = now - dt
                    
                    if diff.days == 0:
                        if diff.seconds < 60:
                            when = "Agora"
                        elif diff.seconds < 3600:
                            when = f"Há {diff.seconds // 60} min"
                        else:
                            when = f"Hoje, há {diff.seconds // 3600} h"
                    elif diff.days == 1:
                        when = "Ontem"
                    else:
                        when = f"{diff.days} dias"
                except:
                    when = "N/A"
            else:
                when = "N/A"
            
            movements_data.append((mov_type, texto, when))
        
        for mov_type, texto, when in movements_data:
            mov_frame = ctk.CTkFrame(chart2_frame, fg_color="transparent")
            mov_frame.pack(fill="x", padx=15, pady=2)
            
            # Cor baseada no tipo
            color = "green" if "Entrada" in mov_type else "red" if "Saída" in mov_type else "blue"
            
            mov_label = ctk.CTkLabel(
                mov_frame, 
                text=f"{texto} — {when}", 
                anchor="w",
                text_color=color,
                font=ctk.CTkFont(size=11)
            )
            mov_label.pack(side="left")
        
        # Espaçamento
        ctk.CTkLabel(chart2_frame, text="").pack(pady=10)
    
    def create_alerts_section(self):
        """Cria a seção de alertas"""
        section_frame, content_frame = self.create_section("🚨 Alertas e Notificações")
        
        # Alertas reais
        alerts_data = []
        
        # Alertas de estoque baixo
        brindes = data_provider.get_brindes()
        estoque_minimo = data_provider.get_configuracao('estoque_minimo', 10)
        
        for brinde in brindes:
            quantidade = brinde.get('quantidade', 0)
            if quantidade <= estoque_minimo:
                if quantidade == 0:
                    alerts_data.append((
                        "🚨", "Estoque Zerado", 
                        f"{brinde.get('descricao', 'Item')}: sem estoque disponível", 
                        "critical"
                    ))
                else:
                    alerts_data.append((
                        "⚠️", "Estoque Baixo", 
                        f"{brinde.get('descricao', 'Item')}: apenas {quantidade} unidades restantes", 
                        "high"
                    ))
        
        # Alertas de movimentações recentes (últimas 24h)
        movimentacoes_recentes = data_provider.get_movimentacoes(limit=10)
        for mov in movimentacoes_recentes:
            data_hora = mov.get('data_hora', '')
            if data_hora:
                try:
                    dt = datetime.fromisoformat(data_hora)
                    now = datetime.now()
                    diff = now - dt
                    
                    if diff.days == 0 and diff.seconds < 86400:  # Últimas 24h
                        tipo = mov.get('tipo', '')
                        if 'transferencia' in tipo:
                            alerts_data.append((
                                "🔄", "Transferência", 
                                f"Transferência de {mov.get('brinde_descricao', 'item')} concluída", 
                                "info"
                            ))
                        elif 'entrada' in tipo:
                            alerts_data.append((
                                "📥", "Entrada", 
                                f"Entrada de {mov.get('quantidade', 0)} {mov.get('brinde_descricao', 'itens')}", 
                                "success"
                            ))
                except:
                    pass
        
        # Limitar a 4 alertas mais importantes
        alerts_data = alerts_data[:4]
        
        # Se não há alertas, mostrar mensagem positiva
        if not alerts_data:
            alerts_data = [
                ("✅", "Sistema OK", "Todos os indicadores estão normais", "success")
            ]
        
        for icon, title, message, alert_type in alerts_data:
            alert_frame = ctk.CTkFrame(content_frame)
            alert_frame.pack(fill="x", pady=5)
            alert_frame.grid_columnconfigure(1, weight=1)
            
            # Ícone
            icon_label = ctk.CTkLabel(alert_frame, text=icon, font=ctk.CTkFont(size=16))
            icon_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            # Conteúdo do alerta
            content_alert_frame = ctk.CTkFrame(alert_frame, fg_color="transparent")
            content_alert_frame.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=10)
            
            # Título do alerta
            alert_title = ctk.CTkLabel(
                content_alert_frame,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            alert_title.pack(anchor="w")
            
            # Mensagem do alerta
            alert_msg = ctk.CTkLabel(
                content_alert_frame,
                text=message,
                font=ctk.CTkFont(size=11),
                text_color=("gray50", "gray50"),
                anchor="w"
            )
            alert_msg.pack(anchor="w")
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        # Atualizar dados e manter atualização periódica
        self.refresh_all()
        self.schedule_auto_refresh()
    
    def refresh_all(self):
        """Reconstrói o conteúdo do dashboard para refletir dados atuais"""
        try:
            # Limpar conteúdo atual do frame principal e recriar UI
            for child in self.frame.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            self.setup_ui()
        except Exception:
            # Em caso de erro, evitar quebra de tela
            pass

    def schedule_auto_refresh(self):
        """Agenda auto-refresh periódico do dashboard"""
        try:
            self.frame.after(self.auto_refresh_ms, self.refresh_all)
        except Exception:
            pass
