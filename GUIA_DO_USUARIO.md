# 📖 Guia do Usuário - Sistema de Controle de Brindes

## 🚀 Como Usar as Novas Funcionalidades

### 🎯 Iniciando o Sistema

```bash
# Para iniciar o sistema:
python main.py

# Ou sem terminal (modo produção):
pythonw main.py
```

A aplicação agora **inicia automaticamente maximizada**! 🖥️

---

## 🎁 Gestão de Brindes - Novas Funcionalidades

### 📄 Paginação Inteligente
- **10 brindes por página** para melhor performance
- **Controles de navegação**:
  - ⏮️ Primeira página
  - ◀️ Página anterior  
  - ▶️ Próxima página
  - ⏭️ Última página
  - **Números das páginas** (clicáveis)
- **Informações em tempo real**: "Página X de Y | Mostrando Z itens"

### ✏️ Edição Rápida com Duplo Clique
- **Duplo clique** em qualquer linha da tabela
- Abre automaticamente o formulário de edição
- Dados **pré-preenchidos** do brinde selecionado

### 🗑️ Exclusão Segura (Apenas Administradores)
- **Botão vermelho** de exclusão visível apenas para admins
- **Confirmação dupla** com detalhes do brinde
- **Proteção de integridade**: Não permite excluir brindes com movimentações
- **Verificação automática** de permissões

---

## ⚙️ Configurações - CRUD Completo

### 📂 Gestão de Categorias
**Criar Nova Categoria:**
1. Acesse **Configurações** → **Categorias**
2. Clique em **"➕ Nova Categoria"**
3. Preencha: Nome e Descrição (opcional)
4. Clique em **"Salvar"**

**Editar Categoria:**
1. Clique no botão **"✏️"** ao lado da categoria
2. Modifique os dados necessários
3. Clique em **"Salvar"**

**Excluir Categoria:**
1. Clique no botão **"🗑️"** ao lado da categoria
2. Confirme a exclusão

### 📏 Gestão de Unidades de Medida
**Criar Nova Unidade:**
1. Acesse **Configurações** → **Unidades**
2. Clique em **"➕ Nova Unidade"**
3. Preencha: Código (máx. 5 chars) e Descrição
4. Clique em **"Salvar"**

**Editar/Excluir:** Mesmo processo das categorias

### 👥 Gestão de Usuários
**Criar Novo Usuário:**
1. Acesse **Configurações** → **Usuários**
2. Clique em **"➕ Novo Usuário"**
3. Preencha todos os campos:
   - **Username**: Nome de login
   - **Nome Completo**: Nome real do usuário
   - **Email**: Email corporativo (opcional)
   - **Filial**: Selecione da lista
   - **Perfil**: Admin, Gestor ou Usuario
   - **Status**: Ativo/Inativo
4. Clique em **"Salvar"**

**Editar Usuário:**
- Clique em **"✏️"** ao lado do usuário
- **Username não pode ser alterado** (proteção)
- Todos os outros campos são editáveis

**Ativar/Desativar Usuário:**
- Clique em **"🔄"** para alternar status
- **Não exclui** o usuário (preserva histórico)

### 🏢 Gestão de Filiais
**Criar Nova Filial:**
1. Acesse **Configurações** → **Filiais**
2. Clique em **"➕ Nova Filial"**
3. Preencha os campos:
   - **Número**: Código da filial (ex: 001)
   - **Nome**: Nome da filial
   - **Endereço**: Endereço completo (opcional)
   - **Cidade**: Cidade da filial
   - **Telefone**: Telefone de contato (opcional)
   - **Status**: Ativa/Inativa
4. Clique em **"Salvar"**

**Editar/Ativar/Desativar:** Mesmo processo dos usuários

---

## 🛡️ Sistema de Permissões

### 👑 Administrador
- **Acesso total** ao sistema
- Pode **excluir brindes**
- Pode **gerenciar usuários**
- Pode **configurar sistema**

### 👨‍💼 Gestor
- **Gestão completa** de brindes
- **Movimentações** de estoque
- **Relatórios** avançados
- **Não pode excluir** brindes

### 👤 Usuário
- **Visualização** de brindes
- **Movimentações básicas**
- **Relatórios simples**
- **Acesso limitado** às configurações

---

## 🎨 Melhorias de Interface

### 🎯 Feedback Visual
- **Cores por status**: Verde (ativo), Vermelho (inativo)
- **Ícones intuitivos**: ✅ Ativo, ❌ Inativo
- **Cores por perfil**: 🔴 Admin, 🟠 Gestor, 🟢 Usuario
- **Alertas de estoque**: Fundo vermelho para estoque baixo

### 📱 Responsividade
- **Tabelas scrolláveis** para muitos dados
- **Formulários adaptativos**
- **Controles otimizados** para diferentes resoluções

### ⚡ Performance
- **Carregamento rápido** com paginação
- **Cache inteligente** para dados frequentes
- **Atualização automática** após operações

---

## 🔧 Funcionalidades do Sistema

### 💾 Backup e Restauração
1. Acesse **Configurações** → **Sistema**
2. **Backup**: Clique em "💾 Backup" e escolha local
3. **Restaurar**: Clique em "📥 Restaurar" e selecione arquivo

### 📋 Logs e Auditoria
- **Todas as operações** são registradas automaticamente
- **Logs de acesso** de usuários
- **Histórico de alterações** em brindes
- **Rastreabilidade completa**

### 📊 Relatórios
- **Estoque atual** por categoria/filial
- **Movimentações** por período
- **Itens com estoque baixo**
- **Auditoria** de operações

---

## 🚨 Dicas Importantes

### ✅ Boas Práticas
1. **Sempre confirme** operações de exclusão
2. **Mantenha backups** regulares
3. **Use filtros** para encontrar itens rapidamente
4. **Verifique permissões** antes de operações críticas

### ⚠️ Cuidados Especiais
1. **Exclusão de brindes**: Só é possível se não houver movimentações
2. **Alteração de usuários**: Username não pode ser alterado
3. **Desativação**: Prefira desativar ao invés de excluir
4. **Backup**: Faça backup antes de grandes alterações

### 🔍 Solução de Problemas
1. **Botão não funciona**: Verifique suas permissões
2. **Lista vazia**: Verifique filtros aplicados
3. **Erro ao salvar**: Verifique campos obrigatórios
4. **Performance lenta**: Use paginação e filtros

---

## 📞 Suporte

### 🆘 Em Caso de Problemas
1. **Verifique logs** do sistema
2. **Reinicie** a aplicação
3. **Verifique permissões** do usuário
4. **Consulte** este guia

### 📈 Melhorias Futuras
- **Relatórios avançados** com gráficos
- **Integração mobile** para tablets
- **API REST** para integrações
- **Backup automático** agendado

---

**🎉 Aproveite o Sistema Atualizado! 🎉**

*Sistema desenvolvido com foco na experiência do usuário e produtividade empresarial.*
