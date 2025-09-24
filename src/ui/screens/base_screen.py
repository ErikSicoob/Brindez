"""
Classe base para todas as telas da aplicação
"""

import customtkinter as ctk

class BaseScreen:
    """Classe base para telas da aplicação"""
    
    def __init__(self, parent, user_manager=None, title="Tela"):
        """Inicializa a tela base"""
        self.parent = parent
        self.user_manager = user_manager
        self.title = title
        self.is_visible = False
        
        # Criar frame principal da tela
        self.frame = ctk.CTkScrollableFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Inicialmente oculta
        self.hide()
    
    def show(self):
        """Mostra a tela"""
        if not self.is_visible:
            self.frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.is_visible = True
            # Aplicar tema aos botões desta tela ao exibir
            try:
                self._apply_button_theme_recursive(self.frame)
            except Exception:
                pass
            self.on_show()
    
    def hide(self):
        """Oculta a tela"""
        if self.is_visible:
            self.frame.grid_remove()
            self.is_visible = False
            self.on_hide()
    
    def on_show(self):
        """Callback chamado quando a tela é mostrada"""
        pass
    
    def on_hide(self):
        """Callback chamado quando a tela é ocultada"""
        pass
    
    def create_title(self, title_text, subtitle_text=None):
        """Cria um título para a tela"""
        title_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Título principal
        title_label = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w")
        
        # Subtítulo (opcional)
        if subtitle_text:
            subtitle_label = ctk.CTkLabel(
                title_frame,
                text=subtitle_text,
                font=ctk.CTkFont(size=14),
                text_color=("gray50", "gray50")
            )
            subtitle_label.pack(anchor="w", pady=(5, 0))
        
        return title_frame
    
    def _apply_button_theme_recursive(self, widget):
        """Aplica o tema padrão de botões a todos CTkButton dentro do widget (recursivo)."""
        try:
            import customtkinter as ctk
        except Exception:
            return
        # Ajuste o próprio widget se for CTkButton
        if isinstance(widget, ctk.CTkButton):
            try:
                text = (widget.cget("text") or "").lower()
            except Exception:
                text = ""
            # Botões de perigo (cancelar/fechar)
            if any(k in text for k in ["cancelar", "fechar"]):
                widget.configure(fg_color=("#cc3333", "#cc3333"), hover_color=("#a82828", "#a82828"))
            else:
                widget.configure(fg_color=("#00AE9D", "#00AE9D"), hover_color=("#008f82", "#008f82"))
        # Recursão em filhos, se possível
        try:
            for child in widget.winfo_children():
                self._apply_button_theme_recursive(child)
        except Exception:
            pass
    
    def create_section(self, title, content_frame_class=None):
        """Cria uma seção com título"""
        section_frame = ctk.CTkFrame(self.frame)
        section_frame.pack(fill="x", pady=(0, 15))
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Título da seção
        section_title = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Frame de conteúdo
        if content_frame_class:
            content_frame = content_frame_class(section_frame)
        else:
            content_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        
        content_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        content_frame.grid_columnconfigure(0, weight=1)
        
        return section_frame, content_frame
