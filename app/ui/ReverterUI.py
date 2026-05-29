#region base projeto
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QPushButton, QLabel, QCheckBox,
)
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import InventarioFuncionalidade
#endregion base projeto


class ReverterUi(QWidget):
    def __init__(self, Historico, Inventario, Gerenciar,GerenciarFuncionarios,Dashboard, Usuario=None):
        """
        Usuario — callable() → int | None: retorna o id do usuário logado
                   (substitui o global UserLogado)
        """
        super().__init__()
        self.GetUser = Usuario

        #topo
        topo = QHBoxLayout()
        for texto, acao in [
            ("Inventário", Inventario),
            ("Adicionar", lambda: Gerenciar("add")),
            ("Remover", lambda: Gerenciar("rem")),
            ("Editar", lambda: Gerenciar("edit")),
            ("Histórico", Historico),
            ("Dashboards", Dashboard),
            ("GerenciarFuncionarios", GerenciarFuncionarios)
        ]:
            btn = QPushButton(texto)
            btn.clicked.connect(acao)
            topo.addWidget(btn)

        #cabeçalho da tabela
        COL_ID       = 120
        COL_TIPO     = 120
        COL_ANTERIOR = 200
        COL_ATUAL    = 100
        COL_CB       = 80

        CabecalhoWidget = QWidget()
        CabecalhoWidget.setStyleSheet("background-color: #005B8C; color: #ffffff;")
        CabecalhoWidget.setAutoFillBackground(True)
        cabecalhoLay = QHBoxLayout(CabecalhoWidget)
        cabecalhoLay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cabecalhoLay.setContentsMargins(8, 4, 8, 4)

        def header(text, width):
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return lbl

        cabecalhoLay.addWidget(header("Identificação",   COL_ID))
        cabecalhoLay.addWidget(header("Tipo alteração",  COL_TIPO))
        cabecalhoLay.addWidget(header("Versão anterior", COL_ANTERIOR))
        cabecalhoLay.addWidget(header("Versão atual",    COL_ATUAL))
        cabecalhoLay.addWidget(header("Reverter",        COL_CB))

        #scroll area
        self.ScrollContent = QWidget()
        self.ListaLayout = QVBoxLayout(self.ScrollContent)
        self.ListaLayout.setSpacing(20)
        self.ListaLayout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(5 * 120)
        scroll.setWidget(self.ScrollContent)

        #montar Layout principal
        corpo = QVBoxLayout()
        corpo.addWidget(CabecalhoWidget)
        corpo.addWidget(scroll)

        base = QVBoxLayout()
        base.addLayout(topo)
        base.addLayout(corpo)
        self.setLayout(base)

        self.AtualizarReverter()

    #helpers

    @staticmethod
    def FormatarDict(d: dict | None) -> str:
        if not d:
            return "—"
        nomes = {
            "Ca": "CA", "TipoEpi": "Tipo", "Dono": "Responsável",
            "Usos": "Usos", "DataDevolucao": "Devolução", "DataDescarte": "Validade",
        }
        linhas = []
        for chave, valor in d.items():
            if isinstance(valor, list):
                valor = ", ".join(valor)
            linhas.append(f"{nomes.get(chave, chave)}: {valor}")
        return "\n".join(linhas)

    #atuar

    def AtualizarReverter(self) -> None:
        while self.ListaLayout.count():
            item = self.ListaLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for registro in InventarioFuncionalidade().ItensReverter():
            linha = self.CriarLinha(registro)
            linha.setFixedHeight(78)
            self.ListaLayout.addWidget(linha)

        self.ListaLayout.addStretch()

    def ReverterAtualizar(self, registroId: int, checked: bool) -> None:
        user = self.GetUser() if self.GetUser else None
        InventarioFuncionalidade().ReverterItem(registroId, checked, user)
        self.AtualizarReverter()

    #construção de linha

    def CriarLinha(self, item) -> QWidget:
        COL_ID       = 120
        COL_TIPO     = 120
        COL_ANTERIOR = 200
        COL_ATUAL    = 100
        COL_CB       = 80

        container = QWidget()
        container.setStyleSheet("background-color: #D9D9D9; color: #000000;")
        Layout = QHBoxLayout(container)
        Layout.setContentsMargins(8, 4, 8, 4)
        Layout.setSpacing(8)

        def col(texto, largura):
            lbl = QLabel(str(texto) if texto else "—")
            lbl.setFixedWidth(largura)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setWordWrap(True)
            return lbl

        Layout.addWidget(col(f"Item #{item.IdItemAlterado}", COL_ID))
        Layout.addWidget(col(item.TiposAlteracao,             COL_TIPO))
        Layout.addWidget(col(self.FormatarDict(item.VersaoAnterior), COL_ANTERIOR))
        Layout.addWidget(col(self.FormatarDict(item.VersaoAtual),    COL_ATUAL))

        cbContainer = QWidget()
        cbContainer.setFixedWidth(COL_CB)
        cbLay = QHBoxLayout(cbContainer)
        cbLay.setContentsMargins(0, 0, 0, 0)
        cb = QCheckBox()
        cb.setChecked(item.revertido or False)
        cb.clicked.connect(
            lambda checked, rid=item.id: self.ReverterAtualizar(rid, checked)
        )
        cbLay.addWidget(cb, alignment=Qt.AlignmentFlag.AlignCenter)
        Layout.addWidget(cbContainer)

        return container