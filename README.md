# 🎁 Sistema de Controle de Brindes

Sistema desktop para controle e gestão de estoque de brindes corporativos, desenvolvido em Python com CustomTkinter.

## 📋 Características

- **Interface Moderna**: Interface gráfica intuitiva com CustomTkinter
- **Multiplataforma**: Compatível com Windows (foco principal)
- **Portable**: Executável standalone sem necessidade de instalação
- **Multi-filial**: Suporte para múltiplas filiais com controle de acesso
- **Relatórios**: Sistema completo de relatórios e análises

## 🚀 Funcionalidades

### ✅ Implementadas (Fase 1 - Estrutura Base)
- [x] Interface principal com menu lateral
- [x] Sistema de navegação entre telas
- [x] Dashboard com indicadores (mock)
- [x] Tela de gestão de brindes
- [x] Tela de movimentações
- [x] Tela de relatórios
- [x] Tela de configurações
- [x] Sistema básico de usuários

### 🔄 Em Desenvolvimento
- [ ] Formulários de cadastro inline
- [ ] Sistema de permissões completo
- [ ] Validações e regras de negócio
- [ ] Integração com SQLite
- [ ] Sistema de relatórios funcional

### 📅 Planejadas
- [ ] Sistema de backup automático
- [ ] Exportação/Importação de dados
- [ ] Sistema de logs e auditoria
- [ ] Otimizações de performance

## 🛠️ Tecnologias

- **Python 3.11+**
- **CustomTkinter 5.2.0** - Interface gráfica moderna
- **SQLite** - Banco de dados local
- **Pillow** - Manipulação de imagens

## 📦 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Instalação das Dependências
```bash
pip install -r requirements.txt
```

### Executar a Aplicação
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
Brindez/
├── main.py                 # Arquivo principal da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Documentação
├── src/                   # Código fonte
│   ├── __init__.py
│   ├── app.py             # Classe principal da aplicação
│   ├── ui/                # Interface gráfica
│   │   ├── __init__.py
│   │   ├── main_window.py # Janela principal
│   │   ├── components/    # Componentes reutilizáveis
│   │   │   ├── __init__.py
│   │   │   ├── header.py  # Cabeçalho
│   │   │   ├── sidebar.py # Menu lateral
│   │   │   └── content_area.py # Área de conteúdo
│   │   └── screens/       # Telas da aplicação
│   │       ├── __init__.py
│   │       ├── base_screen.py    # Classe base
│   │       ├── dashboard.py      # Dashboard
│   │       ├── brindes.py        # Gestão de brindes
│   │       ├── movimentacoes.py  # Movimentações
│   │       ├── relatorios.py     # Relatórios
│   │       └── configuracoes.py  # Configurações
│   └── utils/             # Utilitários
│       ├── __init__.py
│       └── user_manager.py # Gerenciamento de usuários
```

## 👥 Sistema de Usuários

O sistema possui três níveis de acesso:

### 🔴 Admin
- Acesso total ao sistema
- Gestão de usuários e filiais
- Configurações do sistema
- Todos os relatórios

### 🟡 Gestor
- Gestão completa da própria filial
- Movimentações de estoque
- Transferências entre filiais
- Relatórios da filial

### 🟢 Usuário
- Visualização da própria filial
- Saídas de estoque
- Consultas básicas

## 🏢 Multi-filial

- Controle de acesso por filial
- Transferências entre filiais
- Relatórios consolidados (Admin/Matriz)
- Segregação de dados por localização

## 📊 Dashboard

O dashboard apresenta:
- Total de itens em estoque
- Valor total do estoque
- Alertas de estoque baixo
- Movimentações recentes
- Análises por categoria

## ⚙️ Configurações

### Gerais
- Caminho do banco de dados
- Quantidade mínima para alertas
- Configurações de backup

### Gestão
- Categorias de brindes
- Unidades de medida
- Usuários e permissões
- Filiais ativas

## 🔒 Segurança

- Autenticação automática via usuário Windows
- Controle de permissões por perfil
- Auditoria de ações críticas
- Validação de dados de entrada

## 📈 Relatórios

- Estoque atual por filial
- Movimentações por período
- Transferências entre filiais
- Itens com estoque baixo
- Valor de estoque por categoria
- Histórico de movimentações

## 🐛 Desenvolvimento

### Executar em Modo Debug
```bash
python main.py
```

### Estrutura de Desenvolvimento
1. **Fase 1**: Estrutura base e interface ✅
2. **Fase 2**: Funcionalidades core (em andamento)
3. **Fase 3**: Gestão avançada
4. **Fase 4**: Integração com banco
5. **Fase 5**: Finalização e distribuição

## 📝 TODO

- [ ] Implementar formulários de cadastro
- [ ] Criar sistema de validações
- [ ] Integrar com SQLite
- [ ] Implementar sistema de backup
- [ ] Criar executável standalone
- [ ] Testes automatizados
- [ ] Documentação de API

## 🤝 Contribuição

Este é um projeto interno. Para contribuições:

1. Crie uma branch para sua feature
2. Implemente as mudanças
3. Teste thoroughly
4. Submeta um pull request

## 📄 Licença

Projeto interno - Todos os direitos reservados.

## 📞 Suporte

Para suporte técnico, entre em contato com a equipe de desenvolvimento.

---

**Versão**: 1.0.0-beta  
**Última Atualização**: 22/09/2025
