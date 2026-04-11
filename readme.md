# Jornada de Aprendizagem 1 — Sistema de Inventário de EPIs
Indústria parceira: [Guindastes Ribas LTDA](https://www.guindastesribas.com/)

## Objetivo
Estruturar o fluxo correto de descarte de Equipamentos de Proteção Individual (EPI) conforme as regulamentações em vigor, implementando registros eletrônicos das movimentações e descartes como evidência auditável.

---

## Funcionalidades implementadas
- **Inventário de EPIs** — listagem de todos os itens com imagem, identificação, CA, código único, dono, usos, data de devolução, validade e status de descarte; lazy loading por scroll (30 itens por página)
- **Alertas de vencimento** — itens com devolução atrasada ficam em vermelho, próximos de 7 dias em amarelo; pop-up de aviso ao abrir o inventário
- **Pesquisa** — filtragem em tempo real por qualquer campo do item
- **Adicionar item** — formulário com tipo de EPI (QComboBox), CA, responsável, usos, datas de devolução e descarte, área de assinatura digital do funcionário; registra quem cadastrou (`CriadoPor`)
- **Remover item** — soft delete (`Visivel=False`) com registro no histórico de quem removeu
- **Editar item** — seleção por funcionário com preenchimento automático do formulário; registra estado anterior e novo no Histórico e na tabela Reverter
- **Descartar item** — checkbox por item que registra a alteração no histórico com quem descartou
- **Histórico** — log de todas as alterações (adição, edição, remoção, descarte) com versão anterior, versão atual e quem alterou
- **Reverter** — restaura o estado anterior de qualquer item editado via checkbox
- **Login** — autenticação por usuário e senha com sessão global (`UserLogado`); sequência secreta no logo abre tela de criação de conta
- **Criar conta** — tela oculta acessível por sequência de cliques no logo; campos de usuário, senha e cargo
- **Navegação por pilha** — histórico de navegação entre telas (Inventário ↔ Histórico ↔ Gerenciar ↔ Reverter)

---

## Estrutura do projeto
app/
├── data/
│   ├── init.py
│   └── Inventario.py       # modelos ORM e lógica de negócio
└── ui/
├── main.py         # interface gráfica PySide6
└── imgs/               # ícones e imagens da UI

---

## Modelos do banco de dados
| Tabela | Descrição |
|---|---|
| `Inventario` | Registro principal que agrupa itens, contas, histórico e reversões |
| `itens` | Cada EPI individual com seus atributos e quem cadastrou |
| `Historico` | Log imutável de todas as alterações com versão anterior, atual e responsável |
| `Reverter` | Registro de edições que podem ser revertidas via checkbox, com estado anterior e atual |
| `conta` | Usuários do sistema com cargo; vinculados ao inventário |

---

## Fluxo de rastreabilidade
Toda alteração no banco gera um registro em `Historico` com:
- `IdItemAlterado` — id do item afetado
- `TiposAlteracao` — `"edicao"`, `"remocao"` ou `"descarte"`
- `VersaoAnterior` / `VersaoAtual` — estado em JSON antes e depois
- `QuemAlterou` — nome do usuário logado no momento da ação

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
| Flask-Bcrypt | 1.0.1 |
| pyinstaller | 6.15.0 |
| pyinstaller-hooks-contrib | 2025.8 |

---

## Documentação
Canvas base do projeto:
![Canvas base](./PROJECT-MODEL-CANVAS-modelo-A3-em-branco.png)

---

## Ideias gerais / backlog
- [ ] certificado de NR
- [ ] verificar codigo de barra
- [ ] fazer patch pois alterei/removi item e so reiniciando aplicação que ele apareceu no historico
- [ ] funcionalidade remover conta, fazer hash das senhas e outros meios de segurança
- [ ] assinatura digital (do funcionário)(falta salvar num documento)
- [ ] criação de documento para mostrar que funcionario assinou e que o epi é responsabilidade dele em conjunto com a empresa
- [ ] gerar NF para rastreabilidade
- [ ] trocar icone conforme tipo de epi
- [ ] Salvar assinatura digital do funcionário junto ao item no banco
- [ ] Automatizar alertas de trocas e vencimentos (email/notificação)
- [ ] Exclusão verdadeira automática após X meses (`DataDeletar`)
- [ ] Vender a parte de metal do cinto
- [ ] Vender a parte têxtil do cinto
- [ ] Avaliar novos fornecedores
- [ ] Compilar em executável via PyInstaller a versão final
