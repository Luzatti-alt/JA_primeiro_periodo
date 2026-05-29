#region base projeto
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import *
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))

from data.Inventario import ControleFuncionario

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', Path(__file__).parent.parent)
    return str(Path(base) / relative_path)
#endregion base projeto


class GerenciarFuncionariosUI(QWidget):
    PAGESIZE = 30

    def __init__(self, Historico,ControleFuncionarios, Reverter, Gerenciar, Dashboard, Inventario):
        super().__init__()

        self.Offset = 0
        self.Total = 0
        self.Carregando = False
        self.filtroAtivo = ""

        TopoLayout = QHBoxLayout()

        BtnInventario = QPushButton("Inventario")
        BtnInventario.clicked.connect(Inventario)
        AddItem = QPushButton("Adicionar")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem = QPushButton("Remover")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        ReverterBotao = QPushButton("Reverter")
        ReverterBotao.clicked.connect(Reverter)
        BtnHistorico = QPushButton("Historico")
        BtnHistorico.clicked.connect(Historico)
        BtnDashboard = QPushButton("Dashboards")
        BtnDashboard.clicked.connect(Dashboard)

        for btn in (BtnInventario, AddItem, RemItem, EditItem,
                    ReverterBotao, BtnHistorico, BtnDashboard):
            TopoLayout.addWidget(btn)

        COL_AVATAR = 60
        COL_NOME   = 160
        COL_ID     = 40
        COL_CARGO  = 120
        COL_ADM    = 100
        COL_STATUS = 80

        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        CabLayout = QHBoxLayout(FundoTopo)
        CabLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CabLayout.setContentsMargins(8, 4, 8, 4)

        def HeaderLabel(texto, largura):
            lbl = QLabel(texto)
            lbl.setFixedWidth(largura)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        CabLayout.addWidget(HeaderLabel("",         COL_AVATAR))
        CabLayout.addWidget(HeaderLabel("Nome",     COL_NOME))
        CabLayout.addWidget(HeaderLabel("ID",       COL_ID))
        CabLayout.addWidget(HeaderLabel("Cargo",    COL_CARGO))
        CabLayout.addWidget(HeaderLabel("Admissão", COL_ADM))
        CabLayout.addWidget(HeaderLabel("Status",   COL_STATUS))

        ControleFuncionarioLayout = QHBoxLayout()
        AddFuncionario = QPushButton("Adicionar Funcionario")
        AddFuncionario.clicked.connect(lambda: ControleFuncionarios(tipo="add"))
        EditFuncionario = QPushButton("Editar Funcionario")
        EditFuncionario.clicked.connect(lambda: ControleFuncionarios(tipo="edit"))
        RemFuncionario = QPushButton("Remover Funcionario")
        RemFuncionario.clicked.connect(lambda: ControleFuncionarios(tipo="rem"))
        
        ControleFuncionarioLayout.addWidget(AddFuncionario)
        ControleFuncionarioLayout.addWidget(EditFuncionario)
        ControleFuncionarioLayout.addWidget(RemFuncionario)

        PesquisaLayout = QHBoxLayout()
        self.InputPesquisa = QLineEdit()
        self.InputPesquisa.setPlaceholderText("Nome, cargo, matrícula...")
        BtnPesquisar = QPushButton("Pesquisar")
        BtnPesquisar.clicked.connect(
            lambda: self.AtualizarListaFiltrado(self.InputPesquisa.text())
        )
        PesquisaLayout.addWidget(self.InputPesquisa)
        PesquisaLayout.addWidget(BtnPesquisar)

        self.ScrollContent = QWidget()
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setFixedHeight(5 * 80)

        self.ListaLayout = QVBoxLayout(self.ScrollContent)
        self.ListaLayout.setSpacing(4)
        self.ListaLayout.setContentsMargins(0, 0, 0, 0)
        self.ListaLayout.addStretch()
        self.ScrollContent.setLayout(self.ListaLayout)
        self.ScrollArea.setWidget(self.ScrollContent)
        self.ScrollArea.verticalScrollBar().valueChanged.connect(self.OnScroll)

        CorpoLayout = QVBoxLayout()
        CorpoLayout.addWidget(FundoTopo)
        CorpoLayout.addLayout(ControleFuncionarioLayout)
        CorpoLayout.addLayout(PesquisaLayout)
        CorpoLayout.addWidget(self.ScrollArea)

        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(CorpoLayout)
        self.setLayout(BaseLayout)

        self.AtualizarLista()

    def _LimparLista(self):
        while self.ListaLayout.count():
            item = self.ListaLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


    def AtualizarLista(self):
        self.filtroAtivo = ""
        self.Offset = 0
        self.Total = ControleFuncionario().TotalFuncionarios()
        self.Carregando = False

        self.setUpdatesEnabled(False)
        self._LimparLista()
        self.CarregarPagina()
        self.ListaLayout.addStretch()
        self.setUpdatesEnabled(True)

    def CarregarPagina(self):
        if self.Carregando or self.filtroAtivo:
            return
        if self.Offset >= self.Total:
            return

        self.Carregando = True

        ultimo = self.ListaLayout.itemAt(self.ListaLayout.count() - 1)
        if ultimo and ultimo.spacerItem():
            self.ListaLayout.removeItem(ultimo)

        novos = ControleFuncionario().FuncionariosPaginados(
            offset=self.Offset,
            limit=self.PAGESIZE
        )
        for func in novos:
            linha = self.CriarLinhaFuncionario(func)
            linha.setFixedHeight(60)
            self.ListaLayout.addWidget(linha)

        self.Offset += len(novos)
        self.ListaLayout.addStretch()
        self.Carregando = False

    def OnScroll(self, valor):
        barra = self.ScrollArea.verticalScrollBar()
        if valor >= barra.maximum() - 50:
            QTimer.singleShot(0, self.CarregarPagina)

    def AtualizarListaFiltrado(self, filtro):
        self._LimparLista()
        self.filtroAtivo = filtro

        if filtro:
            resultados = ControleFuncionario().Pesquisar(filtro)
        else:
            self.filtroAtivo = ""
            self.Offset = 0
            self.Total = ControleFuncionario().TotalFuncionarios()
            resultados = ControleFuncionario().FuncionariosPaginados(
                offset=0, limit=self.PAGESIZE
            )
            self.Offset = len(resultados)

        for func in resultados:
            linha = self.CriarLinhaFuncionario(func)
            linha.setFixedHeight(60)
            self.ListaLayout.addWidget(linha)

        self.ListaLayout.addStretch()

    def CriarLinhaFuncionario(self, func) -> QWidget:
        COL_AVATAR = 60
        COL_NOME   = 160
        COL_ID     = 40
        COL_CARGO  = 120
        COL_ADM    = 100
        COL_STATUS = 80

        status = (getattr(func, "Status", "") or "").lower()

        # cor de fundo da linha conforme status
        if status == "inativo":
            bg, fg = "#8B0000", "#ffffff"
        elif status in ("ferias", "férias", "licença", "licenca"):
            bg, fg = "#8B6000", "#ffffff"
        else:
            bg, fg = "#D9D9D9", "#000000"

        Container = QWidget()
        # setObjectName + seletor # evita que o estilo vaze para filhos
        Container.setObjectName("LinhaFunc")
        Container.setStyleSheet(
            f"QWidget#LinhaFunc {{ background-color: {bg}; color: {fg}; }}"
        )
        Layout = QHBoxLayout(Container)
        Layout.setContentsMargins(8, 4, 8, 4)
        Layout.setSpacing(0)

        # avatar com iniciais — estilo próprio, não herdado do Container
        Iniciais = "".join(p[0].upper() for p in (func.Nome or "?").split()[:2])
        AvatarLabel = QLabel(Iniciais)
        AvatarLabel.setFixedSize(36, 36)
        AvatarLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        AvatarLabel.setStyleSheet(
            "background-color: #185FA5; color: #E6F1FB;"
            "border-radius: 18px; font-size: 13px; font-weight: 500;"
        )
        ColAvatar = QWidget()
        ColAvatar.setFixedWidth(COL_AVATAR)
        AvLay = QHBoxLayout(ColAvatar)
        AvLay.setContentsMargins(0, 0, 0, 0)
        AvLay.addWidget(AvatarLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(ColAvatar)

        def Col(texto, largura, alinhamento=Qt.AlignmentFlag.AlignCenter):
            lbl = QLabel(str(texto) if texto is not None else "—")
            lbl.setFixedWidth(largura)
            lbl.setAlignment(alinhamento)
            lbl.setWordWrap(True)
            return lbl

        Layout.addWidget(Col(func.Nome,        COL_NOME,  Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
        Layout.addWidget(Col(func.id,          COL_ID))
        Layout.addWidget(Col(func.Cargo,       COL_CARGO))
        Layout.addWidget(Col(func.DataAdmissao,COL_ADM))
        Layout.addWidget(Col(func.Status,      COL_STATUS))

        return Container