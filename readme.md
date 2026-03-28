# Jornada de Aprendizagem 1 — Sistema de Inventário de EPIs

Indústria parceira: [Guindastes Ribas LTDA](https://www.guindastesribas.com/)

## Objetivo

Estruturar o fluxo correto de descarte de Equipamentos de Proteção Individual (EPI) conforme as regulamentações em vigor, implementando registros eletrônicos das movimentações e descartes como evidência auditável.

---

## Funcionalidades implementadas

- **Inventário de EPIs** — listagem de todos os itens com imagem, identificação, CA, código único, dono, usos, data de devolução, validade e status de descarte
- **Adicionar item** — formulário com tipo de EPI (QComboBox), CA, responsável, usos, datas de devolução e descarte
- **Remover item** — soft delete (item permanece no banco com `Visivel=False`)
- **Editar item** — seleção por funcionário com preenchimento automático do formulário
- **Histórico** — registro de todas as alterações (adição, edição, remoção) com versão anterior e versão atual, e opção de reverter
- **Navegação por pilha** — sistema de histórico de navegação entre telas (Inventário → Histórico → Gerenciar)

---

## Estrutura do projeto

```
app/
├── data/
│   ├── __init__.py
│   └── Inventario.py       # modelos ORM e lógica de negócio
└── ui/
    ├── __main__.py         # interface gráfica PySide6
    └── imgs/               # ícones e imagens da UI
```

---

## Modelos do banco de dados

| Tabela | Descrição |
|---|---|
| `inventario` | Registro principal do inventário |
| `itens` | Cada EPI individual com seus atributos |
| `Historico` | Log de todas as alterações realizadas |

---

## Como executar

```bash
# instalar dependências
pip install -r requirements.txt

# popular banco com dados de teste
cd app/data
python Inventario.py

# rodar aplicação
cd app
python -m ui
```

Para recriar o banco do zero (apaga dados existentes):
```bash
cd app/data
python Inventario.py
```

---

## Requerimentos

| Pacote | Versão |
|---|---|
| SQLAlchemy | 2.0.43 |
| PySide6 | 6.10.2 |
| PySide6_Addons | 6.10.2 |
| PySide6_Essentials | 6.10.2 |
| pyinstaller | 6.15.0 |
| pyinstaller-hooks-contrib | 2025.8 |

---

## Documentação

Canvas base do projeto:

![Canvas base](./PROJECT-MODEL-CANVAS-modelo-A3-em-branco.png)

---

## Ideias gerais / backlog

- [ ] Automatizar alertas de trocas e vencimentos
- [ ] Vender a parte de metal do cinto
- [ ] Vender a parte têxtil do cinto
- [ ] Avaliar novos fornecedores
- [ ] Compilar em executável via PyInstaller
