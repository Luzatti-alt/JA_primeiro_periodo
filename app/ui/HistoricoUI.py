#region base projeto
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
import sys
from pathlib import Path
# Adiciona o diretório raiz do projeto ao path e permite usar partes/modulos dcleare outras pastas do projeto
if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import InventarioFuncionalidade #criar init.py para reconhecer modulo
#temp
from data.Inventario import session
#endregion base projeto

class HistoricoUi(QWidget):
    def __init__(self,Reverter, Inventario, Gerenciar):
        super().__init__()
        HistoricoBaseLayout = QVBoxLayout()
        VoltarBotao = QPushButton("Inventario")
        VoltarBotao.clicked.connect(Inventario)
        TopoLayout = QHBoxLayout()
        AddItem  = QPushButton("Adicionar do inventario")
        AddItem.clicked.connect(lambda: Gerenciar("add"))
        RemItem  = QPushButton("Remover do inventario")
        RemItem.clicked.connect(lambda: Gerenciar("rem"))
        EditItem = QPushButton("Editar o inventario")
        EditItem.clicked.connect(lambda: Gerenciar("edit"))
        ReverterBotao = QPushButton("Reverter")
        ReverterBotao.clicked.connect(Reverter)
        TopoLayout.addWidget(VoltarBotao)
        TopoLayout.addWidget(AddItem)
        TopoLayout.addWidget(RemItem)
        TopoLayout.addWidget(EditItem)
        TopoLayout.addWidget(ReverterBotao)

        HisTopoLay = QVBoxLayout()
        FundoTopo = QWidget()
        FundoTopo.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        FundoTopo.setAutoFillBackground(True)
        HistoricoTopoLayout = QHBoxLayout(FundoTopo)
        HistoricoTopoLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        HistoricoTopoLayout.setContentsMargins(8, 4, 8, 4)
        HistoricoTopoLayout.addSpacing(10)
        COL_IMG      = 60
        COL_IDENT    = 80
        COL_DONO     = 120
        COL_ATUAL    = 80
        COL_ANTERIOR = 100
        def HeaderLabel(Text, Width):
            Lbl = QLabel(Text)
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return Lbl
        HistoricoTopoLayout.addWidget(HeaderLabel("", COL_IMG))           # espaço da imagem
        HistoricoTopoLayout.addWidget(HeaderLabel("Identificação", COL_IDENT))
        HistoricoTopoLayout.addWidget(HeaderLabel("Dono",          COL_DONO))
        HistoricoTopoLayout.addWidget(HeaderLabel("versão anterior",     COL_ANTERIOR))
        HistoricoTopoLayout.addWidget(HeaderLabel("versão atual",  COL_ATUAL))
        HisTopoLay.addWidget(FundoTopo)

        self.ScrollContent = QWidget()
        ScrollArea = QScrollArea()
        ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setFixedHeight(5 * 120)
        self.ListaItensLayout = QVBoxLayout(self.ScrollContent)
        self.ListaItensLayout.setSpacing(20)
        self.ListaItensLayout.setContentsMargins(0, 0, 0, 0)

        DbItens = InventarioFuncionalidade().ItensHistorico()
        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)
        self.ListaItensLayout.addStretch()
        self.ScrollContent.setLayout(self.ListaItensLayout)
        ScrollArea.setWidget(self.ScrollContent)
        HistoricoBaseLayout.addLayout(HisTopoLay)
        HistoricoBaseLayout.addWidget(ScrollArea)

        BaseLayout = QVBoxLayout()
        BaseLayout.addLayout(TopoLayout)
        BaseLayout.addLayout(HistoricoBaseLayout)
        self.setLayout(BaseLayout)
    def FormatarDictTexto(self,d):
        if not d:
            return "—"

        NomeAmigaveis = {
            "Ca": "CA",
            "TipoEpi": "Tipo",
            "Dono": "Responsável",
            "Usos": "Usos",
            "DataDevolucao": "Devolução",
            "DataDescarte": "Validade"
        }

        linhas = []
        for chave, valor in d.items():
            nome = NomeAmigaveis.get(chave, chave)

            # tratar lista (ex: usos)
            if isinstance(valor, list):
                valor = ", ".join(valor)

            linhas.append(f"{nome}: {valor}")

        return "\n".join(linhas)
    def AtualizarHistorico(self):
        while self.ListaItensLayout.count():
            item = self.ListaItensLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        DbItens = InventarioFuncionalidade().ItensHistorico()

        for Item in DbItens:
            Linha = self.CriarLinhaItem(Item)
            Linha.setFixedHeight(78)
            self.ListaItensLayout.addWidget(Linha)

        self.ListaItensLayout.addStretch()
    def HistoricoEAtualizar(self, Id, Checked):
        InventarioFuncionalidade().HistoricoItem(Id, Checked)
        self.AtualizarHistorico()
    def CriarLinhaItem(self, Item) -> QWidget:
        COL_ID       = 120
        COL_TIPO     = 120
        COL_ANTERIOR = 200
        COL_ATUAL    = 100
        COL_CB       = 80

        Container = QWidget()
        Container.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        Layout = QHBoxLayout(Container)
        Layout.setContentsMargins(8, 4, 8, 4)
        Layout.setSpacing(8)

        def Col(Text, Width):
            Lbl = QLabel(str(Text) if Text else "—")
            Lbl.setFixedWidth(Width)
            Lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            Lbl.setWordWrap(True)
            return Lbl

        Layout.addWidget(Col(f"Item #{Item.IdItemAlterado}", COL_ID))
        Layout.addWidget(Col(Item.TiposAlteracao,             COL_TIPO))
        Layout.addWidget(Col(self.FormatarDictTexto(Item.VersaoAnterior), COL_ANTERIOR))
        Layout.addWidget(Col(self.FormatarDictTexto(Item.VersaoAtual), COL_ATUAL))

        return Container
