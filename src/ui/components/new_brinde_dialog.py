"""
Dialogo especializado para cadastro de novo brinde, com regras atuais
"""

import customtkinter as ctk
from tkinter import messagebox
from ...data.data_provider import data_provider
from ...utils.validators import BrindeValidator, ValidationError, BusinessRuleError
from .form_dialog import FormDialog

class NewBrindeDialog(FormDialog):
    """Diálogo dedicado para criar um novo Brinde seguindo as regras atuais.
    - Usa checkbox_group_quantities para alocação por filial
    - Valida dados com BrindeValidator
    - Cria múltiplos registros quando houver alocação em várias filiais
    """
    def __init__(self, parent, user_manager=None, on_success=None):
        self.user_manager = user_manager
        self.on_success = on_success
        fields = self._build_fields()
        super().__init__(
            parent,
            title="➕ Novo Brinde",
            fields=fields,
            on_submit=self._on_submit,
            on_cancel=None,
            show_header=False,
        )

    def _safe_filial_names(self):
        try:
            return [f.get('nome', 'N/A') for f in data_provider.get_filiais() if f and f.get('nome')]
        except Exception:
            return []

    def _build_fields(self):
        return [
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
                'type': 'checkbox_group_quantities',
                'required': True,
                'options': self._safe_filial_names()
            },
        ]

    def show_with_defaults(self):
        initial_values = {}
        try:
            user = self.user_manager.get_current_user() if self.user_manager else None
            if user and user.get('filial'):
                initial_values['filial'] = {user.get('filial'): 0}
        except Exception:
            pass
        self.show(initial_values)

    # Callback chamado pelo FormDialog.submit
    def _on_submit(self, data):
        try:
            # Validar dados com regras atuais
            validated_data = BrindeValidator.validate_brinde_data(
                data,
                data_provider.get_categorias(),
                data_provider.get_unidades_medida(),
                self._safe_filial_names(),
            )

            # Anexar usuário
            try:
                user = self.user_manager.get_current_user() if self.user_manager else None
                if user:
                    validated_data['usuario_cadastro'] = user.get('username', 'admin')
            except Exception:
                pass

            # Alocação por filial: campo 'filial' vem como dict {filial: quantidade}
            alocacoes = validated_data.pop('filial', {}) or {}
            quantidade_total = int(validated_data.get('quantidade', 0))

            if not isinstance(alocacoes, dict) or not alocacoes:
                raise ValidationError("Selecione pelo menos uma filial e informe a quantidade para cada uma.")

            soma_alocada = sum(int(v or 0) for v in alocacoes.values())
            if soma_alocada != quantidade_total:
                raise ValidationError(
                    f"A soma das quantidades por filial ({soma_alocada}) deve ser igual à quantidade total digitada ({quantidade_total})."
                )

            # Criar registros por filial
            for filial, qtd in alocacoes.items():
                qtd_int = int(qtd or 0)
                if qtd_int < 0:
                    raise ValidationError("Quantidade por filial não pode ser negativa.")
                if qtd_int == 0:
                    continue
                brinde_data = validated_data.copy()
                brinde_data['filial'] = filial
                brinde_data['quantidade'] = qtd_int
                data_provider.create_brinde(brinde_data)

            # Sucesso
            if callable(self.on_success):
                try:
                    self.on_success()
                except Exception:
                    pass
            messagebox.showinfo("Sucesso", "Brinde(s) cadastrado(s) com sucesso!")
            return True

        except (ValidationError, BusinessRuleError) as e:
            messagebox.showerror("Erro de Validação", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar brinde: {e.__class__.__name__}: {e}")
            return False
