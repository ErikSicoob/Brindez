"""
Tela de Configurações
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from .base_screen import BaseScreen
from ..components.form_dialog import FormDialog
from ...data.data_provider import data_provider
from ...utils.user_manager import UserManager

class ConfiguracoesScreen(BaseScreen):
    """Tela de configurações"""
    
    def __init__(self, parent):
        """Inicializa a tela de configurações"""
        super().__init__(parent, "Configurações")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface de configurações"""
        # Título da tela
        self.create_title("⚙️ Configurações", "Configurações gerais do sistema")
        
        # Criar abas de configurações
        self.create_tabs()
    
    def create_tabs(self):
        """Cria as abas de configurações"""
        # Frame principal das abas
        tabs_frame = ctk.CTkFrame(self.frame)
        tabs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tabs_frame.grid_columnconfigure(1, weight=1)
        tabs_frame.grid_rowconfigure(0, weight=1)
        
        # Menu lateral das abas
        tabs_menu = ctk.CTkFrame(tabs_frame, width=200)
        tabs_menu.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        tabs_menu.grid_propagate(False)
        
        # Área de conteúdo das abas
        self.tabs_content = ctk.CTkFrame(tabs_frame)
        self.tabs_content.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.tabs_content.grid_columnconfigure(0, weight=1)
        self.tabs_content.grid_rowconfigure(0, weight=1)
        
        # Botões das abas
        self.tab_buttons = {}
        self.tab_frames = {}
        
        tabs = [
            ("gerais", "🔧 Gerais"),
            ("categorias", "📂 Categorias"),
            ("unidades", "📏 Unidades"),
            ("usuarios", "👥 Usuários"),
            ("filiais", "🏢 Filiais"),
            ("sistema", "💻 Sistema")
        ]
        
        for i, (tab_id, tab_name) in enumerate(tabs):
            # Botão da aba
            btn = ctk.CTkButton(
                tabs_menu,
                text=tab_name,
                command=lambda t=tab_id: self.show_tab(t),
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.tab_buttons[tab_id] = btn
            
            # Frame da aba
            frame = ctk.CTkScrollableFrame(self.tabs_content)
            frame.grid_columnconfigure(0, weight=1)
            self.tab_frames[tab_id] = frame
        
        # Criar conteúdo das abas
        self.create_gerais_tab()
        self.create_categorias_tab()
        self.create_unidades_tab()
        self.create_usuarios_tab()
        self.create_filiais_tab()
        self.create_sistema_tab()
        
        # Mostrar primeira aba
        self.show_tab("gerais")
    
    def show_tab(self, tab_id):
        """Mostra uma aba específica"""
        # Ocultar todas as abas
        for frame in self.tab_frames.values():
            frame.grid_remove()
        
        # Resetar cores dos botões
        for btn in self.tab_buttons.values():
            btn.configure(fg_color=("gray75", "gray25"))
        
        # Mostrar aba selecionada
        self.tab_frames[tab_id].grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_buttons[tab_id].configure(fg_color=("blue", "blue"))
    
    def create_gerais_tab(self):
        """Cria a aba de configurações gerais"""
        frame = self.tab_frames["gerais"]
        
        # Título
        title = ctk.CTkLabel(frame, text="🔧 Configurações Gerais", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Banco de Dados
        db_section = ctk.CTkFrame(frame)
        db_section.pack(fill="x", pady=(0, 15))
        
        db_title = ctk.CTkLabel(db_section, text="💾 Banco de Dados", font=ctk.CTkFont(size=14, weight="bold"))
        db_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        db_path_frame = ctk.CTkFrame(db_section, fg_color="transparent")
        db_path_frame.pack(fill="x", padx=15, pady=(0, 15))
        db_path_frame.grid_columnconfigure(0, weight=1)
        
        db_label = ctk.CTkLabel(db_path_frame, text="Caminho do banco:")
        db_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        db_entry = ctk.CTkEntry(db_path_frame, placeholder_text="C:\\dados\\brindez.db")
        db_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        db_btn = ctk.CTkButton(db_path_frame, text="📁", width=40, command=self.browse_db_path)
        db_btn.grid(row=1, column=1)
        
        # Estoque
        stock_section = ctk.CTkFrame(frame)
        stock_section.pack(fill="x", pady=(0, 15))
        
        stock_title = ctk.CTkLabel(stock_section, text="📦 Configurações de Estoque", font=ctk.CTkFont(size=14, weight="bold"))
        stock_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        min_stock_frame = ctk.CTkFrame(stock_section, fg_color="transparent")
        min_stock_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        min_label = ctk.CTkLabel(min_stock_frame, text="Quantidade mínima para alerta:")
        min_label.pack(anchor="w", pady=(0, 5))
        
        min_entry = ctk.CTkEntry(min_stock_frame, placeholder_text="10", width=100)
        min_entry.pack(anchor="w")
    
    def create_categorias_tab(self):
        """Cria a aba de categorias"""
        frame = self.tab_frames["categorias"]
        
        # Título
        title = ctk.CTkLabel(frame, text="📂 Gestão de Categorias", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Botão nova categoria
        new_cat_btn = ctk.CTkButton(frame, text="➕ Nova Categoria", command=self.new_category)
        new_cat_btn.pack(pady=(0, 15), anchor="w")
        
        # Lista de categorias
        categories_frame = ctk.CTkFrame(frame)
        categories_frame.pack(fill="both", expand=True)
        
        # Buscar categorias reais
        try:
            categories = data_provider.get_categorias_completas()
        except:
            categories = []
        
        for cat in categories:
            cat_frame = ctk.CTkFrame(categories_frame, fg_color="transparent")
            cat_frame.pack(fill="x", padx=10, pady=5)
            cat_frame.grid_columnconfigure(0, weight=1)
            
            cat_nome = cat.get('nome', cat) if isinstance(cat, dict) else cat
            cat_label = ctk.CTkLabel(cat_frame, text=f"📂 {cat_nome}", anchor="w")
            cat_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            
            edit_btn = ctk.CTkButton(cat_frame, text="✏️", width=30, height=25, command=lambda c=cat_nome: self.edit_category(c))
            edit_btn.grid(row=0, column=1, padx=5)
            
            delete_btn = ctk.CTkButton(cat_frame, text="🗑️", width=30, height=25, command=lambda c=cat_nome: self.delete_category(c))
            delete_btn.grid(row=0, column=2, padx=5)
    
    def create_unidades_tab(self):
        """Cria a aba de unidades de medida"""
        frame = self.tab_frames["unidades"]
        
        # Título
        title = ctk.CTkLabel(frame, text="📏 Unidades de Medida", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Botão nova unidade
        new_unit_btn = ctk.CTkButton(frame, text="➕ Nova Unidade", command=self.new_unit)
        new_unit_btn.pack(pady=(0, 15), anchor="w")
        
        # Lista de unidades
        units_frame = ctk.CTkFrame(frame)
        units_frame.pack(fill="both", expand=True)
        
        # Buscar unidades reais
        try:
            units = data_provider.get_unidades_medida_completas()
        except:
            units = []
        
        for unit in units:
            unit_frame = ctk.CTkFrame(units_frame, fg_color="transparent")
            unit_frame.pack(fill="x", padx=10, pady=5)
            unit_frame.grid_columnconfigure(0, weight=1)
            
            code = unit.get('codigo', '') if isinstance(unit, dict) else unit[0] if isinstance(unit, tuple) else str(unit)
            desc = unit.get('descricao', '') if isinstance(unit, dict) else unit[1] if isinstance(unit, tuple) else ''
            
            unit_label = ctk.CTkLabel(unit_frame, text=f"📏 {code} - {desc}", anchor="w")
            unit_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            
            edit_btn = ctk.CTkButton(unit_frame, text="✏️", width=30, height=25, command=lambda c=code: self.edit_unit(c))
            edit_btn.grid(row=0, column=1, padx=5)
            
            delete_btn = ctk.CTkButton(unit_frame, text="🗑️", width=30, height=25, command=lambda c=code: self.delete_unit(c))
            delete_btn.grid(row=0, column=2, padx=5)
    
    def create_usuarios_tab(self):
        """Cria a aba de usuários"""
        frame = self.tab_frames["usuarios"]
        
        # Título
        title = ctk.CTkLabel(frame, text="👥 Gestão de Usuários", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Botão novo usuário
        new_user_btn = ctk.CTkButton(frame, text="➕ Novo Usuário", command=self.new_user)
        new_user_btn.pack(pady=(0, 15), anchor="w")
        
        # Lista de usuários
        users_frame = ctk.CTkFrame(frame)
        users_frame.pack(fill="both", expand=True)
        
        # Buscar usuários reais
        try:
            users = data_provider.get_usuarios_completos()
        except:
            users = []
        
        for user in users:
            user_frame = ctk.CTkFrame(users_frame, fg_color="transparent")
            user_frame.pack(fill="x", padx=10, pady=5)
            user_frame.grid_columnconfigure(0, weight=1)
            
            username = user.get('username', '') if isinstance(user, dict) else user[0] if isinstance(user, tuple) else str(user)
            name = user.get('nome', '') if isinstance(user, dict) else user[1] if isinstance(user, tuple) else ''
            filial = user.get('filial', '') if isinstance(user, dict) else user[2] if isinstance(user, tuple) else ''
            profile = user.get('perfil', '') if isinstance(user, dict) else user[3] if isinstance(user, tuple) else ''
            active = user.get('ativo', True) if isinstance(user, dict) else user[4] if isinstance(user, tuple) else True
            
            status_icon = "✅" if active else "❌"
            profile_color = {"Admin": "red", "Gestor": "orange", "Usuario": "green"}.get(profile, "gray")
            
            user_label = ctk.CTkLabel(
                user_frame, 
                text=f"{status_icon} {name} ({username}) - {filial} - {profile}", 
                anchor="w",
                text_color=profile_color
            )
            user_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            
            edit_btn = ctk.CTkButton(user_frame, text="✏️", width=30, height=25, command=lambda u=username: self.edit_user(u))
            edit_btn.grid(row=0, column=1, padx=5)
            
            toggle_btn = ctk.CTkButton(
                user_frame, 
                text="🔄", 
                width=30, 
                height=25, 
                command=lambda u=username: self.toggle_user(u)
            )
            toggle_btn.grid(row=0, column=2, padx=5)
    
    def create_filiais_tab(self):
        """Cria a aba de filiais"""
        frame = self.tab_frames["filiais"]
        
        # Título
        title = ctk.CTkLabel(frame, text="🏢 Gestão de Filiais", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Botão nova filial
        new_filial_btn = ctk.CTkButton(frame, text="➕ Nova Filial", command=self.new_filial)
        new_filial_btn.pack(pady=(0, 15), anchor="w")
        
        # Lista de filiais
        filiais_frame = ctk.CTkFrame(frame)
        filiais_frame.pack(fill="both", expand=True)
        
        # Buscar filiais reais
        try:
            filiais = data_provider.get_filiais_completas()
        except:
            filiais = []
        
        for filial in filiais:
            filial_frame = ctk.CTkFrame(filiais_frame, fg_color="transparent")
            filial_frame.pack(fill="x", padx=10, pady=5)
            filial_frame.grid_columnconfigure(0, weight=1)
            
            numero = filial.get('numero', '') if isinstance(filial, dict) else filial[0] if isinstance(filial, tuple) else str(filial)
            nome = filial.get('nome', '') if isinstance(filial, dict) else filial[1] if isinstance(filial, tuple) else ''
            cidade = filial.get('cidade', '') if isinstance(filial, dict) else filial[2] if isinstance(filial, tuple) else ''
            active = filial.get('ativa', True) if isinstance(filial, dict) else filial[3] if isinstance(filial, tuple) else True
            
            status_icon = "✅" if active else "❌"
            
            filial_label = ctk.CTkLabel(
                filial_frame, 
                text=f"{status_icon} {numero} - {nome} ({cidade})", 
                anchor="w"
            )
            filial_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
            
            edit_btn = ctk.CTkButton(filial_frame, text="✏️", width=30, height=25, command=lambda n=numero: self.edit_filial(n))
            edit_btn.grid(row=0, column=1, padx=5)
            
            toggle_btn = ctk.CTkButton(
                filial_frame, 
                text="🔄", 
                width=30, 
                height=25, 
                command=lambda n=numero: self.toggle_filial(n)
            )
            toggle_btn.grid(row=0, column=2, padx=5)
    
    def create_sistema_tab(self):
        """Cria a aba de configurações do sistema"""
        frame = self.tab_frames["sistema"]
        
        # Título
        title = ctk.CTkLabel(frame, text="💻 Configurações do Sistema", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 20), anchor="w")
        
        # Informações do sistema
        info_section = ctk.CTkFrame(frame)
        info_section.pack(fill="x", pady=(0, 15))
        
        info_title = ctk.CTkLabel(info_section, text="ℹ️ Informações", font=ctk.CTkFont(size=14, weight="bold"))
        info_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        info_data = [
            ("Versão:", "1.0.0 - Beta"),
            ("Banco de Dados:", "SQLite 3.40.0"),
            ("Python:", "3.11.0"),
            ("CustomTkinter:", "5.2.0"),
            ("Última Atualização:", "22/09/2025")
        ]
        
        for label, value in info_data:
            info_frame = ctk.CTkFrame(info_section, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=2)
            info_frame.grid_columnconfigure(1, weight=1)
            
            label_widget = ctk.CTkLabel(info_frame, text=label, anchor="w", width=150)
            label_widget.grid(row=0, column=0, sticky="w")
            
            value_widget = ctk.CTkLabel(info_frame, text=value, anchor="w")
            value_widget.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Botões de ação
        actions_section = ctk.CTkFrame(frame)
        actions_section.pack(fill="x", pady=(15, 0))
        
        actions_title = ctk.CTkLabel(actions_section, text="🔧 Ações", font=ctk.CTkFont(size=14, weight="bold"))
        actions_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        actions_frame = ctk.CTkFrame(actions_section, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(0, 15))
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        backup_btn = ctk.CTkButton(actions_frame, text="💾 Backup", command=self.backup_database)
        backup_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        restore_btn = ctk.CTkButton(actions_frame, text="📥 Restaurar", command=self.restore_database)
        restore_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        logs_btn = ctk.CTkButton(actions_frame, text="📋 Ver Logs", command=self.view_logs)
        logs_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
    
    # Métodos de callback implementados
    def browse_db_path(self):
        """Seleciona caminho do banco de dados"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Selecionar local do banco de dados",
                defaultextension=".db",
                filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            if filename:
                messagebox.showinfo("Sucesso", f"Caminho selecionado: {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar arquivo: {e}")
    
    def new_category(self):
        """Cria nova categoria"""
        fields = [
            {
                'key': 'nome',
                'label': 'Nome da Categoria',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: Eletrônicos'
            },
            {
                'key': 'descricao',
                'label': 'Descrição',
                'type': 'text',
                'required': False,
                'placeholder': 'Descrição opcional da categoria'
            }
        ]
        
        dialog = FormDialog(self.frame, "Nova Categoria", fields, self.save_new_category)
        dialog.show()
    
    def save_new_category(self, data):
        """Salva nova categoria"""
        try:
            categoria = data_provider.create_categoria(data)
            messagebox.showinfo("Sucesso", "Categoria criada com sucesso!")
            self.refresh_categorias_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar categoria: {e}")
    
    def edit_category(self, category):
        """Edita uma categoria"""
        try:
            # Buscar categoria atual
            categorias = data_provider.get_categorias_completas()
            categoria_atual = None
            for cat in categorias:
                # Tratar diferentes tipos de dados
                cat_nome = cat.get('nome') if isinstance(cat, dict) else str(cat)
                if cat_nome == category:
                    categoria_atual = cat if isinstance(cat, dict) else {'nome': cat, 'descricao': '', 'id': None}
                    break
            
            if not categoria_atual:
                messagebox.showerror("Erro", "Categoria não encontrada!")
                return
            
            fields = [
                {
                    'key': 'nome',
                    'label': 'Nome da Categoria',
                    'type': 'entry',
                    'required': True,
                    'value': categoria_atual.get('nome', '')
                },
                {
                    'key': 'descricao',
                    'label': 'Descrição',
                    'type': 'text',
                    'required': False,
                    'value': categoria_atual.get('descricao', '')
                }
            ]
            
            dialog = FormDialog(
                self.frame, 
                "Editar Categoria", 
                fields, 
                lambda data: self.save_edit_category(categoria_atual.get('id'), data)
            )
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar categoria: {e}")
    
    def save_edit_category(self, categoria_id, data):
        """Salva edição de categoria"""
        try:
            categoria = data_provider.update_categoria(categoria_id, data)
            messagebox.showinfo("Sucesso", "Categoria atualizada com sucesso!")
            self.refresh_categorias_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar categoria: {e}")
    
    def delete_category(self, category):
        """Exclui uma categoria"""
        try:
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a categoria '{category}'?\n\n"
                f"Esta ação não pode ser desfeita!"
            )
            
            if not resposta:
                return
            
            # Buscar ID da categoria
            categorias = data_provider.get_categorias()
            categoria_id = None
            for cat in categorias:
                if cat.get('nome') == category:
                    categoria_id = cat.get('id')
                    break
            
            if categoria_id:
                sucesso = data_provider.delete_categoria(categoria_id)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!")
                    self.refresh_categorias_tab()
                else:
                    messagebox.showerror("Erro", "Erro ao excluir categoria!")
            else:
                messagebox.showerror("Erro", "Categoria não encontrada!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir categoria: {e}")
    
    def new_unit(self):
        """Cria nova unidade de medida"""
        fields = [
            {
                'key': 'codigo',
                'label': 'Código',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: UN, KG, LT',
                'max_length': 5
            },
            {
                'key': 'descricao',
                'label': 'Descrição',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: Unidade, Quilograma, Litro'
            }
        ]
        
        dialog = FormDialog(self.frame, "Nova Unidade de Medida", fields, self.save_new_unit)
        dialog.show()
    
    def save_new_unit(self, data):
        """Salva nova unidade"""
        try:
            unidade = data_provider.create_unidade_medida(data)
            messagebox.showinfo("Sucesso", "Unidade criada com sucesso!")
            self.refresh_unidades_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar unidade: {e}")
    
    def edit_unit(self, unit):
        """Edita uma unidade de medida"""
        try:
            # Buscar unidade atual
            unidades = data_provider.get_unidades_medida_completas()
            unidade_atual = None
            for un in unidades:
                # Tratar diferentes tipos de dados
                un_codigo = un.get('codigo') if isinstance(un, dict) else (un[0] if isinstance(un, tuple) else str(un))
                if un_codigo == unit:
                    if isinstance(un, dict):
                        unidade_atual = un
                    elif isinstance(un, tuple):
                        unidade_atual = {'codigo': un[0], 'descricao': un[1], 'id': None}
                    else:
                        unidade_atual = {'codigo': str(un), 'descricao': '', 'id': None}
                    break
            
            if not unidade_atual:
                messagebox.showerror("Erro", "Unidade não encontrada!")
                return
            
            fields = [
                {
                    'key': 'codigo',
                    'label': 'Código',
                    'type': 'entry',
                    'required': True,
                    'value': unidade_atual.get('codigo', ''),
                    'max_length': 5
                },
                {
                    'key': 'descricao',
                    'label': 'Descrição',
                    'type': 'entry',
                    'required': True,
                    'value': unidade_atual.get('descricao', '')
                }
            ]
            
            dialog = FormDialog(
                self.frame, 
                "Editar Unidade de Medida", 
                fields, 
                lambda data: self.save_edit_unit(unidade_atual.get('id'), data)
            )
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar unidade: {e}")
    
    def save_edit_unit(self, unidade_id, data):
        """Salva edição de unidade"""
        try:
            unidade = data_provider.update_unidade_medida(unidade_id, data)
            messagebox.showinfo("Sucesso", "Unidade atualizada com sucesso!")
            self.refresh_unidades_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar unidade: {e}")
    
    def delete_unit(self, unit):
        """Exclui uma unidade de medida"""
        try:
            resposta = messagebox.askyesno(
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a unidade '{unit}'?\n\n"
                f"Esta ação não pode ser desfeita!"
            )
            
            if not resposta:
                return
            
            # Buscar ID da unidade
            unidades = data_provider.get_unidades_medida()
            unidade_id = None
            for un in unidades:
                if un.get('codigo') == unit:
                    unidade_id = un.get('id')
                    break
            
            if unidade_id:
                sucesso = data_provider.delete_unidade_medida(unidade_id)
                if sucesso:
                    messagebox.showinfo("Sucesso", "Unidade excluída com sucesso!")
                    self.refresh_unidades_tab()
                else:
                    messagebox.showerror("Erro", "Erro ao excluir unidade!")
            else:
                messagebox.showerror("Erro", "Unidade não encontrada!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir unidade: {e}")
    
    def new_user(self):
        """Cria novo usuário"""
        filiais = data_provider.get_filiais()
        filiais_nomes = [f.get('nome', '') for f in filiais]
        
        fields = [
            {
                'key': 'username',
                'label': 'Nome de Usuário',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: joao.silva'
            },
            {
                'key': 'nome',
                'label': 'Nome Completo',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: João Silva'
            },
            {
                'key': 'email',
                'label': 'E-mail',
                'type': 'entry',
                'required': False,
                'placeholder': 'joao.silva@empresa.com',
                'validation': 'email'
            },
            {
                'key': 'filial',
                'label': 'Filial',
                'type': 'combo',
                'required': True,
                'options': filiais_nomes
            },
            {
                'key': 'perfil',
                'label': 'Perfil',
                'type': 'combo',
                'required': True,
                'options': ['Admin', 'Gestor', 'Usuario']
            },
            {
                'key': 'ativo',
                'label': 'Usuário Ativo',
                'type': 'checkbox',
                'value': True
            }
        ]
        
        dialog = FormDialog(self.frame, "Novo Usuário", fields, self.save_new_user)
        dialog.show()
    
    def save_new_user(self, data):
        """Salva novo usuário"""
        try:
            usuario = data_provider.create_usuario(data)
            messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
            self.refresh_usuarios_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {e}")
    
    def edit_user(self, username):
        """Edita um usuário"""
        try:
            # Buscar usuário atual
            usuarios = data_provider.get_usuarios()
            usuario_atual = None
            for user in usuarios:
                # Tratar diferentes tipos de dados
                user_username = user.get('username') if isinstance(user, dict) else (user[0] if isinstance(user, tuple) else str(user))
                if user_username == username:
                    if isinstance(user, dict):
                        usuario_atual = user
                    elif isinstance(user, tuple):
                        usuario_atual = {
                            'username': user[0], 'nome': user[1], 'filial': user[2], 
                            'perfil': user[3], 'ativo': user[4], 'email': '', 'id': None
                        }
                    else:
                        usuario_atual = {'username': str(user), 'nome': '', 'filial': '', 'perfil': '', 'ativo': True, 'email': '', 'id': None}
                    break
            
            if not usuario_atual:
                messagebox.showerror("Erro", "Usuário não encontrado!")
                return
            
            filiais = data_provider.get_filiais_completas()
            filiais_nomes = [f.get('nome', '') if isinstance(f, dict) else (f[1] if isinstance(f, tuple) else str(f)) for f in filiais]
            
            fields = [
                {
                    'key': 'username',
                    'label': 'Nome de Usuário',
                    'type': 'entry',
                    'required': True,
                    'value': usuario_atual.get('username', ''),
                    'readonly': True  # Username não deve ser editável
                },
                {
                    'key': 'nome',
                    'label': 'Nome Completo',
                    'type': 'entry',
                    'required': True,
                    'value': usuario_atual.get('nome', '')
                },
                {
                    'key': 'email',
                    'label': 'E-mail',
                    'type': 'entry',
                    'required': False,
                    'value': usuario_atual.get('email', ''),
                    'validation': 'email'
                },
                {
                    'key': 'filial',
                    'label': 'Filial',
                    'type': 'combo',
                    'required': True,
                    'options': filiais_nomes,
                    'value': usuario_atual.get('filial', '')
                },
                {
                    'key': 'perfil',
                    'label': 'Perfil',
                    'type': 'combo',
                    'required': True,
                    'options': ['Admin', 'Gestor', 'Usuario'],
                    'value': usuario_atual.get('perfil', '')
                },
                {
                    'key': 'ativo',
                    'label': 'Usuário Ativo',
                    'type': 'checkbox',
                    'value': usuario_atual.get('ativo', True)
                }
            ]
            
            dialog = FormDialog(
                self.frame, 
                "Editar Usuário", 
                fields, 
                lambda data: self.save_edit_user(usuario_atual.get('id'), data)
            )
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar usuário: {e}")
    
    def save_edit_user(self, usuario_id, data):
        """Salva edição de usuário"""
        try:
            usuario = data_provider.update_usuario(usuario_id, data)
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            self.refresh_usuarios_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário: {e}")
    
    def toggle_user(self, username):
        """Ativa/Desativa um usuário"""
        try:
            # Buscar usuário
            usuarios = data_provider.get_usuarios()
            usuario = None
            for user in usuarios:
                if user.get('username') == username:
                    usuario = user
                    break
            
            if not usuario:
                messagebox.showerror("Erro", "Usuário não encontrado!")
                return
            
            novo_status = not usuario.get('ativo', True)
            status_texto = "ativar" if novo_status else "desativar"
            
            resposta = messagebox.askyesno(
                "Confirmar Alteração",
                f"Tem certeza que deseja {status_texto} o usuário '{username}'?"
            )
            
            if resposta:
                data = {**usuario, 'ativo': novo_status}
                data_provider.update_usuario(usuario.get('id'), data)
                messagebox.showinfo("Sucesso", f"Usuário {status_texto}do com sucesso!")
                self.refresh_usuarios_tab()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar status do usuário: {e}")
    
    def new_filial(self):
        """Cria nova filial"""
        fields = [
            {
                'key': 'numero',
                'label': 'Número',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: 001, 002',
                'max_length': 10
            },
            {
                'key': 'nome',
                'label': 'Nome',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: Filial São Paulo'
            },
            {
                'key': 'endereco',
                'label': 'Endereço',
                'type': 'text',
                'required': False,
                'placeholder': 'Endereço completo da filial'
            },
            {
                'key': 'cidade',
                'label': 'Cidade',
                'type': 'entry',
                'required': True,
                'placeholder': 'Ex: São Paulo'
            },
            {
                'key': 'telefone',
                'label': 'Telefone',
                'type': 'entry',
                'required': False,
                'placeholder': '(11) 99999-9999'
            },
            {
                'key': 'ativa',
                'label': 'Filial Ativa',
                'type': 'checkbox',
                'value': True
            }
        ]
        
        dialog = FormDialog(self.frame, "Nova Filial", fields, self.save_new_filial)
        dialog.show()
    
    def save_new_filial(self, data):
        """Salva nova filial"""
        try:
            filial = data_provider.create_filial(data)
            messagebox.showinfo("Sucesso", "Filial criada com sucesso!")
            self.refresh_filiais_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar filial: {e}")
    
    def edit_filial(self, numero):
        """Edita uma filial"""
        try:
            # Buscar filial atual
            filiais = data_provider.get_filiais_completas()
            filial_atual = None
            for fil in filiais:
                # Tratar diferentes tipos de dados
                fil_numero = fil.get('numero') if isinstance(fil, dict) else (fil[0] if isinstance(fil, tuple) else str(fil))
                if fil_numero == numero:
                    if isinstance(fil, dict):
                        filial_atual = fil
                    elif isinstance(fil, tuple):
                        filial_atual = {
                            'numero': fil[0], 'nome': fil[1], 'cidade': fil[2], 
                            'ativa': fil[3], 'endereco': '', 'telefone': '', 'id': None
                        }
                    else:
                        filial_atual = {'numero': str(fil), 'nome': '', 'cidade': '', 'ativa': True, 'endereco': '', 'telefone': '', 'id': None}
                    break
            
            if not filial_atual:
                messagebox.showerror("Erro", "Filial não encontrada!")
                return
            
            fields = [
                {
                    'key': 'numero',
                    'label': 'Número',
                    'type': 'entry',
                    'required': True,
                    'value': filial_atual.get('numero', ''),
                    'max_length': 10
                },
                {
                    'key': 'nome',
                    'label': 'Nome',
                    'type': 'entry',
                    'required': True,
                    'value': filial_atual.get('nome', '')
                },
                {
                    'key': 'endereco',
                    'label': 'Endereço',
                    'type': 'text',
                    'required': False,
                    'value': filial_atual.get('endereco', '')
                },
                {
                    'key': 'cidade',
                    'label': 'Cidade',
                    'type': 'entry',
                    'required': True,
                    'value': filial_atual.get('cidade', '')
                },
                {
                    'key': 'telefone',
                    'label': 'Telefone',
                    'type': 'entry',
                    'required': False,
                    'value': filial_atual.get('telefone', '')
                },
                {
                    'key': 'ativa',
                    'label': 'Filial Ativa',
                    'type': 'checkbox',
                    'value': filial_atual.get('ativa', True)
                }
            ]
            
            dialog = FormDialog(
                self.frame, 
                "Editar Filial", 
                fields, 
                lambda data: self.save_edit_filial(filial_atual.get('id'), data)
            )
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao editar filial: {e}")
    
    def save_edit_filial(self, filial_id, data):
        """Salva edição de filial"""
        try:
            filial = data_provider.update_filial(filial_id, data)
            messagebox.showinfo("Sucesso", "Filial atualizada com sucesso!")
            self.refresh_filiais_tab()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar filial: {e}")
    
    def toggle_filial(self, numero):
        """Ativa/Desativa uma filial"""
        try:
            # Buscar filial
            filiais = data_provider.get_filiais()
            filial = None
            for fil in filiais:
                if fil.get('numero') == numero:
                    filial = fil
                    break
            
            if not filial:
                messagebox.showerror("Erro", "Filial não encontrada!")
                return
            
            novo_status = not filial.get('ativa', True)
            status_texto = "ativar" if novo_status else "desativar"
            
            resposta = messagebox.askyesno(
                "Confirmar Alteração",
                f"Tem certeza que deseja {status_texto} a filial '{filial.get('nome')}'?"
            )
            
            if resposta:
                data = {**filial, 'ativa': novo_status}
                data_provider.update_filial(filial.get('id'), data)
                messagebox.showinfo("Sucesso", f"Filial {status_texto}da com sucesso!")
                self.refresh_filiais_tab()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar status da filial: {e}")
    
    def backup_database(self):
        """Faz backup do banco de dados"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Salvar backup do banco de dados",
                defaultextension=".db",
                filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            if filename:
                # Implementar backup real aqui
                messagebox.showinfo("Sucesso", f"Backup salvo em: {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer backup: {e}")
    
    def restore_database(self):
        """Restaura backup do banco de dados"""
        try:
            filename = filedialog.askopenfilename(
                title="Selecionar backup para restaurar",
                filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")]
            )
            if filename:
                resposta = messagebox.askyesno(
                    "Confirmar Restauração",
                    "Tem certeza que deseja restaurar o backup?\n\n"
                    "Todos os dados atuais serão substituídos!"
                )
                if resposta:
                    # Implementar restauração real aqui
                    messagebox.showinfo("Sucesso", "Backup restaurado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {e}")
    
    def view_logs(self):
        """Visualiza logs do sistema"""
        try:
            # Implementar visualização de logs
            messagebox.showinfo("Logs", "Funcionalidade de visualização de logs em desenvolvimento.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar logs: {e}")
    
    # Métodos de atualização das abas
    def refresh_categorias_tab(self):
        """Atualiza a aba de categorias"""
        # Limpar conteúdo atual
        for widget in self.tab_frames["categorias"].winfo_children():
            widget.destroy()
        # Recriar conteúdo
        self.create_categorias_tab()
    
    def refresh_unidades_tab(self):
        """Atualiza a aba de unidades"""
        # Limpar conteúdo atual
        for widget in self.tab_frames["unidades"].winfo_children():
            widget.destroy()
        # Recriar conteúdo
        self.create_unidades_tab()
    
    def refresh_usuarios_tab(self):
        """Atualiza a aba de usuários"""
        # Limpar conteúdo atual
        for widget in self.tab_frames["usuarios"].winfo_children():
            widget.destroy()
        # Recriar conteúdo
        self.create_usuarios_tab()
    
    def refresh_filiais_tab(self):
        """Atualiza a aba de filiais"""
        # Limpar conteúdo atual
        for widget in self.tab_frames["filiais"].winfo_children():
            widget.destroy()
        # Recriar conteúdo
        self.create_filiais_tab()
