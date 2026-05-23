#region base projeto
from PySide6.QtCore import Qt, QDate, QPoint
from PySide6.QtGui import QColor, QPixmap, QPainter, QPen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit,
)
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))
from data.Inventario import InventarioFuncionalidade, ControleFuncionario
#endregion base projeto


def _pasta_assinaturas() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent
    pasta = base / "assinaturas"
    pasta.mkdir(exist_ok=True)
    return pasta


class AssinaturaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 150)
        self.Canvas = QPixmap(800, 350)
        self.Canvas.fill(QColor("#ffffff"))
        self.UltimoPonto = QPoint()
        self.Desenhando = False
        self.setStyleSheet("border: 2px solid #005B8C; background-color: #ffffff;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.Desenhando = True
            self.UltimoPonto = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if not self.Desenhando:
            return
        painter = QPainter(self.Canvas)
        pen = QPen(QColor("#000000"), 2, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.UltimoPonto, event.position().toPoint())
        painter.end()
        self.UltimoPonto = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.Desenhando = False

    def paintEvent(self, event):
        QPainter(self).drawPixmap(0, 0, self.Canvas)

    def limpar(self) -> None:
        self.Canvas.fill(QColor("#ffffff"))
        self.update()

    def vazio(self) -> bool:
        img = self.Canvas.toImage()
        for y in range(img.height()):
            for x in range(img.width()):
                if QColor(img.pixel(x, y)).lightness() < 200:
                    return False
        return True

    def pixmap(self) -> QPixmap:
        return self.Canvas.copy()

    def SalvarAssinatura(self, nome_func: str, data: str, caminho: str = "") -> bool:
        if not caminho:
            caminho = f"{nome_func}_{data}_assinatura.png"
        return self.Canvas.save(caminho, "PNG")


TIPOSEPI = [
    "capacete", "luva", "cinto", "bota",
    "alabarte", "manquito", "oculos",
    "protetor auricolar", "colete refletivo",
]


class GerenciadorInventario(QWidget):
    def __init__(self, Historico, Inventario, Dashboard, Reverter,
                 ControleFuncionarios, Usuario=None):
        super().__init__()
        self.IrInventario = Inventario
        self.IrReverter   = Reverter
        self.GetUser      = Usuario

        self.BtnInventario           = QPushButton("Inventário")
        self.BtnAdd                  = QPushButton("Adicionar")
        self.BtnRem                  = QPushButton("Remover")
        self.BtnEdit                 = QPushButton("Editar")
        self.BtnReverter             = QPushButton("Reverter")
        self.BtnHistorico            = QPushButton("Histórico")
        self.BtnDashboard            = QPushButton("Dashboards")
        self.BtnControleFuncionarios = QPushButton("ControleFuncionarios")

        self.BtnInventario.clicked.connect(self.IrInventario)
        self.BtnReverter.clicked.connect(self.IrReverter)
        self.BtnHistorico.clicked.connect(Historico)
        self.BtnDashboard.clicked.connect(Dashboard)
        self.BtnControleFuncionarios.clicked.connect(ControleFuncionarios)
        self.BtnAdd.clicked.connect(lambda: self.AtualizarTipo("add"))
        self.BtnRem.clicked.connect(lambda: self.AtualizarTipo("rem"))
        self.BtnEdit.clicked.connect(lambda: self.AtualizarTipo("edit"))

        topo = QHBoxLayout()
        for Btn in (
            self.BtnInventario, self.BtnAdd, self.BtnRem,
            self.BtnEdit, self.BtnReverter, self.BtnHistorico,
            self.BtnDashboard, self.BtnControleFuncionarios,
        ):
            topo.addWidget(Btn)

        self.Conteudo = QWidget()
        self.ConteudoLayout = QHBoxLayout(self.Conteudo)

        base = QVBoxLayout()
        base.addLayout(topo)
        base.addWidget(self.Conteudo)
        self.setLayout(base)
        
    def LimparConteudo(self) -> None:
        while self.ConteudoLayout.count():
            Item = self.ConteudoLayout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
            elif Item.layout():
                self.LimparLayout(Item.layout())

    def LimparLayout(self, Layout) -> None:
        while Layout.count():
            Item = Layout.takeAt(0)
            if Item.widget():
                Item.widget().deleteLater()
            elif Item.layout():
                self.LimparLayout(Item.layout())

    def User(self) -> int | None:
        return self.GetUser() if self.GetUser else None

    @staticmethod
    def ConstruirComboItens(combo: QComboBox) -> list[int]:
        #Popula combo com itens do inventário (para rem/edit). Retorna IDs."""
        registros = InventarioFuncionalidade().RemListaFuncionarios()
        ids: list[int] = []
        for ItemId, nome in registros:
            combo.addItem(f"ID: {ItemId}  —  {nome}", userData=ItemId)
            ids.append(ItemId)
        return ids

    @staticmethod
    def ConstruirListaFUncionarios(combo: QComboBox) -> None:
        #Popula combo com nomes dos Funcionarios cadastrados."""
        combo.clear()
        for func in ControleFuncionario().ListarFuncionarios():
            combo.addItem(func.Nome, userData=func.id)

    #tela: Adicionar

    def Add(self) -> None:
        self.LimparConteudo()

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)

        self.InputCa   = QLineEdit()
        self.InputTipo = QComboBox()
        self.InputTipo.addItems(TIPOSEPI)

        self.InputDono = QComboBox()
        self.ConstruirListaFUncionarios(self.InputDono)

        self.InputUsos      = QLineEdit()
        self.InputDevolucao = QDateEdit(calendarPopup=True)
        self.InputDevolucao.setDate(QDate.currentDate())
        self.InputDescarte  = QDateEdit(calendarPopup=True)
        self.InputDescarte.setDate(QDate.currentDate())

        form.addRow("CA:",             self.InputCa)
        form.addRow("Tipo de EPI:",    self.InputTipo)
        form.addRow("Responsável:",    self.InputDono)
        form.addRow("Usos:",           self.InputUsos)
        form.addRow("Data devolução:", self.InputDevolucao)
        form.addRow("Data descarte:",  self.InputDescarte)

        assinaturaLay = QVBoxLayout()
        LblAss = QLabel("Assinatura do Funcionário:")
        LblAss.setStyleSheet("color: #ffffff; border: none;")
        self.AreaAssinatura = AssinaturaWidget()
        BtnLimparAss = QPushButton("Limpar assinatura")
        BtnLimparAss.clicked.connect(self.AreaAssinatura.limpar)
        assinaturaLay.addWidget(LblAss)
        assinaturaLay.addWidget(self.AreaAssinatura)
        assinaturaLay.addWidget(BtnLimparAss)
        form.addRow(assinaturaLay)

        BtnConfirmar = QPushButton("Adicionar Item")
        BtnConfirmar.clicked.connect(self.ConfirmarAdd)
        form.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(FormWidget)

    def ConfirmarAdd(self) -> None:
        if not self.InputCa.text().strip() or self.InputDono.count() == 0:
            return
        ca   = self.InputCa.text().strip()
        dono = self.InputDono.currentText()
        data = str(QDate.currentDate().toPython())

        InventarioFuncionalidade().AddItem(
            registro=self.User(),
            ca=ca,
            Registrodata=data,
            tipo_epi=self.InputTipo.currentText(),
            dono=dono,
            usos=[u.strip() for u in self.InputUsos.text().split(",") if u.strip()],
            data_descarte=str(self.InputDescarte.date().toPython()),
            data_devolucao=str(self.InputDevolucao.date().toPython()),
        )
        if not self.AreaAssinatura.vazio():
            pasta = _pasta_assinaturas()
            self.AreaAssinatura.SalvarAssinatura(
                nome_func=dono,
                data=data,
                caminho=str(pasta / f"{dono}_{data}.png"),
            )
        self.IrInventario()

    #tela: Remover

    def Rem(self) -> None:
        self.LimparConteudo()

        self.ComboRem = QComboBox()
        self.ConstruirComboItens(self.ComboRem)

        BtnRem = QPushButton("Remover Item")
        BtnRem.clicked.connect(self.ConfirmarRem)

        self.ConteudoLayout.addWidget(self.ComboRem)
        self.ConteudoLayout.addWidget(BtnRem)

    def ConfirmarRem(self) -> None:
        if self.ComboRem.count() == 0:
            return
        ItemId = self.ComboRem.currentData()
        InventarioFuncionalidade().RemItem(ItemId, self.User())
        self.IrInventario()

    #tela: Editar

    def Edit(self) -> None:
        self.LimparConteudo()

        container = QVBoxLayout()

        SelecaoWidget = QWidget()
        SelecaoForm   = QFormLayout(SelecaoWidget)

        self.ComboEdit = QComboBox()
        self.ConstruirComboItens(self.ComboEdit)

        BtnSelecionar = QPushButton("Selecionar")
        BtnSelecionar.clicked.connect(self.selecionarEdicao)
        SelecaoForm.addRow("Item:", self.ComboEdit)
        SelecaoForm.addRow(BtnSelecionar)
        container.addWidget(SelecaoWidget)

        self.FormEditWidget = QWidget()
        self.FormEditWidget.hide()
        formEdit = QFormLayout(self.FormEditWidget)
        formEdit.setSpacing(10)

        self.EditCa   = QLineEdit()
        self.EditTipo = QComboBox()
        self.EditTipo.addItems(TIPOSEPI)

        self.EditDono = QComboBox()
        self.ConstruirListaFUncionarios(self.EditDono)

        self.EditUsos      = QLineEdit()
        self.EditDevolucao = QDateEdit(calendarPopup=True)
        self.EditDevolucao.setDate(QDate.currentDate())
        self.EditDescarte  = QDateEdit(calendarPopup=True)
        self.EditDescarte.setDate(QDate.currentDate())

        formEdit.addRow("CA:",             self.EditCa)
        formEdit.addRow("Tipo de EPI:",    self.EditTipo)
        formEdit.addRow("Responsável:",    self.EditDono)
        formEdit.addRow("Usos:",           self.EditUsos)
        formEdit.addRow("Data devolução:", self.EditDevolucao)
        formEdit.addRow("Data descarte:",  self.EditDescarte)

        container.addWidget(self.FormEditWidget)

        BtnEditar = QPushButton("Confirmar edição")
        BtnEditar.clicked.connect(self.ConfirmarEdicao)
        container.addWidget(BtnEditar)

        self.ConteudoLayout.addLayout(container)

    def selecionarEdicao(self) -> None:
        ItemId = self.ComboEdit.currentData()
        Item   = InventarioFuncionalidade().SelFuncionario(ItemId)
        if not Item:
            return
        self.EditCa.setText(Item.Ca)
        self.EditTipo.setCurrentText(Item.TipoEpi)
        idx = self.EditDono.findText(Item.Dono)
        if idx >= 0:
            self.EditDono.setCurrentIndex(idx)
        self.EditUsos.setText(Item.Usosformatado)
        self.FormEditWidget.show()

    def ConfirmarEdicao(self) -> None:
        ItemId = self.ComboEdit.currentData()
        InventarioFuncionalidade().EditItem(
            self.User(),
            ItemId,
            self.EditCa.text().strip(),
            self.EditTipo.currentText(),
            self.EditDono.currentText(),
            [u.strip() for u in self.EditUsos.text().split(",") if u.strip()],
            str(self.EditDevolucao.date().toPython()),
            str(self.EditDescarte.date().toPython()),
        )
        self.IrInventario()

    def AtualizarTipo(self, tipo: str) -> None:
        MapaBtn  = {"add": self.BtnAdd, "rem": self.BtnRem, "edit": self.BtnEdit}
        mapaAcao = {"add": self.Add,    "rem": self.Rem,    "edit": self.Edit}

        for Btn in MapaBtn.values():
            Btn.setVisible(True)

        if tipo in MapaBtn:
            MapaBtn[tipo].setVisible(False)
            mapaAcao[tipo]()