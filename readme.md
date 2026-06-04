# Sistema de Controle de EPI Inteligente
Indústria parceira: [Guindastes Ribas LTDA](https://www.guindastesribas.com/)

## Objetivo
Estruturar o fluxo correto de descarte de Equipamentos de Proteção Individual (EPI) conforme as regulamentações em vigor, implementando registros eletrônicos completos das movimentações e descartes como evidência auditável.

---

## Funcionalidades implementadas

### Autenticação e Contas
- **Login** — autenticação por usuário e senha com hash bcrypt; bloqueio de conta após tentativas inválidas (15 minutos); sessão global por `UserLogado`
- **Criar conta** — tela oculta acessível por sequência secreta de cliques no logo; campos de usuário, senha e cargo (`admin` / `operador`)
- **Excluir conta** — acessível por sequência secreta distinta; lista contas existentes por combo e remove pelo nome de usuário

### Inventário de EPIs
- **Listagem** — exibe todos os itens ativos com imagem, tipo de EPI, CA, código único, ID, dono, usos, data de devolução, validade e checkbox de descarte; lazy loading por scroll (30 itens por página)
- **Alertas de vencimento** — itens com devolução atrasada ficam em vermelho; dentro de 7 dias ficam em amarelo; pop-up de aviso é exibido uma vez ao abrir o inventário
- **Pesquisa** — filtragem em tempo real por CA, código único, tipo de EPI, dono, data de descarte ou data de devolução

### CRUD de Itens
- **Adicionar** — formulário com tipo de EPI (9 tipos disponíveis), CA, responsável (lista de funcionários cadastrados), usos, datas de devolução e descarte, área de assinatura digital do funcionário; gera código único automático; registra `CriadoPor`
- **Remover** — soft delete (`Visivel=False`) com agendamento de exclusão permanente em 1 ano (`DataDeletar`); registra no Histórico e na tabela Reverter quem removeu
- **Editar** — seleção por item (combo ID + dono), preenchimento automático do formulário; atualiza código único; registra estado anterior e novo no Histórico e em Reverter
- **Descartar** — checkbox por item; registra data de devolução real e quem descartou no Histórico; suporta desfazer o descarte

### Funcionários
- **Gerenciar Funcionários** — listagem paginada (30 por página) com avatar de iniciais, nome, ID, cargo, data de admissão e status; scroll infinito; pesquisa por nome, cargo, e-mail ou status; cores por status (vermelho = inativo, amarelo = férias/licença)
- **Adicionar funcionário** — formulário com nome, e-mail, cargo e data de admissão
- **Editar funcionário** — carrega dados atuais; permite alterar nome, e-mail, cargo e status (`Ativo | Inativo | Férias | Licença`)
- **Remover funcionário** — seleção por combo com ID; exclusão permanente do banco

### Auditoria
- **Histórico** — log imutável de todas as alterações (adição, edição, remoção, descarte, reversão) com versão anterior, versão atual, tipo de alteração e quem alterou; timestamp automático (`DataAlteracao`)
- **Reverter** — restaura o estado anterior de qualquer item editado ou removido via checkbox; registra a reversão no Histórico; itens já revertidos não aparecem na lista

### Dashboard
- **Visão geral** — KPIs de EPIs ativos, descartados, itens em atraso, próximos à devolução e entregas no mês; gráfico de pizza por tipo de EPI; gráfico de barras horizontais com top 8 funcionários; histórico de alterações dos últimos 30 dias
- **Dashboard de atrasos** — lista apenas itens com devolução atrasada, com gráfico de barras mostrando dias de atraso por item
- **Dashboard pessoal** — selecionável por combo; exibe KPIs individuais (ativos, descartados, em atraso, em dia) e gráfico de pizza com status dos EPIs do funcionário; atualização automática a cada 30 segundos

### Assinatura Digital
- **Área de assinatura** — widget de desenho com mouse (canvas 800×350); suporta limpar e verificar se está vazia; salva em PNG na pasta `assinaturas/` com nome `{funcionário}_{data}.png` ao adicionar um item

---

## Estrutura do projeto

```
app/
├── data/
│   ├── __init__.py
│   ├── Inventario.py          # modelos ORM (SQLAlchemy) e toda a lógica de negócio
│   ├── ComprovarCadastro.py   # (em desenvolvimento) geração de PDF com assinatura
│   ├── CodigoBarras.py        # (a implementar)
│   ├── db.log                 # log de alterações do banco
│   └── GuindastesRibasDB.db   # banco SQLite gerado automaticamente
└── ui/
    ├── __init__.py
    ├── main.py                # ponto de entrada; GerenciadorJanelas (QStackedWidget)
    ├── ContasUI.py            # telas de Login, CriarConta e ExcluirConta
    ├── InventarioUI.py        # tela principal de listagem de EPIs
    ├── ControleInventarioUI.py# telas de Adicionar / Remover / Editar itens
    ├── HistoricoUI.py         # tela de log de alterações
    ├── ReverterUI.py          # tela de reversão de alterações
    ├── DashBoardUI.py         # dashboards (geral, atrasos, pessoal) com matplotlib
    ├── GerenciarFuncionarioUi.py # listagem e pesquisa de funcionários
    ├── ControleFunc.py        # CRUD de funcionários (add, edit, rem)
    └── imgs/                  # ícones e imagens da interface

executavel/
├── build/                     # gerado pelo PyInstaller
└── dist/                      # executável final

assinaturas/                   # PNGs das assinaturas salvas ao cadastrar itens
build.txt                      # comando de build PyInstaller
main.spec                      # spec do PyInstaller
readme.md                      # este arquivo
requirements.txt               # dependências do projeto
```

---

## Modelos do banco de dados

| Tabela | Descrição |
|---|---|
| `Inventario` | Entidade raiz que agrupa itens, contas, histórico e reversões via relacionamentos |
| `itens` | Cada EPI individual: CA, tipo, dono, usos, datas, código único, visibilidade, descarte e quem cadastrou |
| `Funcionarios` | Dados do funcionário: nome, e-mail, cargo, status, data de admissão e listas de EPIs em dia/atrasados |
| `Historico` | Log imutável de todas as alterações com versão anterior, versão atual, responsável e timestamp |
| `Reverter` | Snapshot de edições revertíveis; marcado como `revertido=True` após restauração |
| `conta` | Usuários do sistema com senha hashada (bcrypt) e cargo; vinculados ao inventário |

---

## Fluxo de rastreabilidade

Toda operação que altera dados gera registros duplos:

**Histórico** — imutável, para auditoria:
- `IdItemAlterado` — ID do item afetado
- `TiposAlteracao` — `"adicao"`, `"edicao"`, `"remocao"`, `"descarte"` ou `"reversao"`
- `VersaoAnterior` / `VersaoAtual` — estado em JSON antes e depois
- `QuemAlterou` — nome do usuário logado no momento
- `DataAlteracao` — data ISO gerada automaticamente

**Reverter** — mutável, para restauração:
- Mesmos campos do Histórico mais `revertido` (bool)
- Ao reverter, o item é restaurado e um novo registro de `"reversao"` é gravado no Histórico

---

## Código único de item

Gerado automaticamente ao adicionar ou editar um item:

```
{3 primeiras letras do dono}{4 primeiros dígitos do CA}{dia do descarte}{dia da devolução}
```

Exemplo: dono `Carlos`, CA `CA-1023`, descarte `2025-12-15`, devolução `2025-06-30` → `CARCA-102153060`

---

## Tipos de EPI disponíveis

`capacete`, `luva`, `cinto`, `bota`, `alabarte`, `manquito`, `oculos`, `protetor auricolar`, `colete refletivo`

---

## Como executar

```bash
# instalar dependências
pip install -r requirements.txt

# popular banco com dados de teste (apaga banco existente)
cd app/data
python Inventario.py

# rodar a aplicação
cd app
python -m ui
```

Credenciais de teste geradas pelo `fake_data()`:
- **Usuário:** `admin` | **Senha:** `123456`

---

## Como compilar (PyInstaller)

```bash
# ver comando completo em build.txt
pyinstaller main.spec
# executável gerado em executavel/dist/
```

---

## Requerimentos

| Pacote | Versão |
|---|---|
| SQLAlchemy | 2.0.43 |
| PySide6 | 6.10.2 |
| PySide6_Addons | 6.10.2 |
| PySide6_Essentials | 6.10.2 |
| matplotlib | (qualquer compatível com PySide6) |
| Flask-Bcrypt | 1.0.1 |
| bcrypt | 5.0.0 |
| pyinstaller | 6.15.0 |
| pyinstaller-hooks-contrib | 2025.8 |

---

## Bugs conhecidos / limitações atuais

- Item adicionado ou removido só aparece no Histórico após reiniciar a aplicação (patch pendente)
- `ComprovarCadastro.py` ainda não gera o PDF com a assinatura do funcionário
- Assinatura digital é salva apenas como PNG local; não está vinculada ao item no banco de dados
- Código único não garante unicidade em caso de colisão de dados (mesmo dono, CA e datas)

---

## Backlog / Ideias futuras

- [ ] Gerar PDF de entrega de EPI com assinatura digital do funcionário (NR)
- [ ] Salvar assinatura digital vinculada ao item no banco de dados
- [ ] Verificação de código de barras do CA
- [ ] Trocar ícone do item conforme tipo de EPI
- [ ] Automatizar alertas de vencimento por e-mail ou notificação
- [ ] Exclusão permanente automática após 1 ano (`DataDeletar` já implementado no banco)
- [ ] Hash de senhas para contas de operadores (bcrypt já presente para admin)
- [ ] Funcionalidade completa de remoção de conta (UI já existe, fluxo de confirmação pendente)
- [ ] Gerar NF para rastreabilidade de descartes
- [ ] Avaliar novos fornecedores de EPI
- [ ] Vender parte metálica e têxtil do cinto separadamente
- [ ] Compilar versão final em executável via PyInstaller
