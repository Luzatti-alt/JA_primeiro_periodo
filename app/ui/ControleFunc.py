#region base projeto
from PySide6.QtCore import Qt,QTimer,QDate
from PySide6.QtGui import QColor, QPalette, QIcon
from PySide6.QtWidgets import QApplication,QDateEdit, QFormLayout,QComboBox,QLineEdit, QPushButton, QWidget, QVBoxLayout,QHBoxLayout, QStackedWidget
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))

from data.Inventario import ControleFuncionario

class ControleFuncionariosUI(QWidget):
    def __init__(self,tipo, Historico,GerenciarFuncionarios, Reverter, Gerenciar, Dashboard, Inventario):
        super().__init__()
        self.tipo = tipo
        self.IrInventario = Inventario
        self.IrReverter   = Reverter

        self.BtnInventario           = QPushButton("Inventário")
        self.BtnAdd                  = QPushButton("Adicionar")
        self.BtnRem                  = QPushButton("Remover")
        self.BtnEdit                 = QPushButton("Editar")
        self.BtnReverter             = QPushButton("Reverter")
        self.BtnHistorico            = QPushButton("Histórico")
        self.BtnDashboard            = QPushButton("Dashboards")
        self.BtnGerenciarFuncionarios = QPushButton("GerenciarFuncionarios")

        self.BtnInventario.clicked.connect(self.IrInventario)
        self.BtnReverter.clicked.connect(self.IrReverter)
        self.BtnHistorico.clicked.connect(Historico)
        self.BtnDashboard.clicked.connect(Dashboard)
        self.BtnGerenciarFuncionarios.clicked.connect(GerenciarFuncionarios)
        self.BtnAdd.clicked.connect(lambda: self.AtualizarTipo("add"))
        self.BtnRem.clicked.connect(lambda: self.AtualizarTipo("rem"))
        self.BtnEdit.clicked.connect(lambda: self.AtualizarTipo("edit"))

        topo = QHBoxLayout()
        for Btn in (
            self.BtnInventario, self.BtnAdd, self.BtnRem,
            self.BtnEdit, self.BtnReverter, self.BtnHistorico,
            self.BtnDashboard, self.BtnGerenciarFuncionarios,
        ):
            topo.addWidget(Btn)

        self.Conteudo = QWidget()
        self.ConteudoLayout = QHBoxLayout(self.Conteudo)

        base = QVBoxLayout()
        base.addLayout(topo)
        base.addWidget(self.Conteudo)
        self.setLayout(base)

    #elementos gerais de controle
    def AtualizarTipo(self, tipo):
        self.tipo = tipo
        MapaBtn  = {"add": self.BtnAdd, "rem": self.BtnRem, "edit": self.BtnEdit}
        mapaAcao = {"add": self.add,    "rem": self.remove, "edit": self.edit}

        for Btn in MapaBtn.values():
            Btn.setVisible(True)

        if tipo in MapaBtn:
            MapaBtn[tipo].setVisible(False)
            mapaAcao[tipo]()

    @staticmethod
    def ConstruirListaFUncionarios(combo: QComboBox) -> None:
        #Popula combo com nomes dos Funcionarios cadastrados."""
        combo.clear()
        for func in ControleFuncionario().ListarFuncionarios():
            combo.addItem(func.Nome, userData=func.id)


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

    #Ui especifica conforme tipos
    
    def add(self)-> None:
        self.LimparConteudo()
        cargos = ["operario","gerente"]#ADD mais dps

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)

        InputNome = QLineEdit()
        InputEmail = QLineEdit()
        InputCargo = QComboBox()
        InputCargo.addItems(cargos)
        data = QDateEdit(calendarPopup=True)
        data.setDate(QDate.currentDate())
        form.addRow("Nome",InputNome)
        form.addRow("Email",InputEmail)
        form.addRow("Cargo",InputCargo)

        BtnConfirmar = QPushButton("Adicionar Funcionário")
        BtnConfirmar.clicked.connect(lambda:(
            ControleFuncionario().Contratar(
            nome=InputNome.text(),
            email=InputEmail.text(),
            cargo=InputCargo.currentText(),
            data_admissao=str(data.date().toPython())
        ),
        self.IrInventario()
        )
        )
        form.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(FormWidget)



    def remove(self)-> None:
        self.LimparConteudo()

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)
        #aparecer select da lista de funcionarios+btn de confirmar
        ListaFuncionarios = QComboBox()
        self.ConstruirListaFUncionarios(ListaFuncionarios)
        #Inventario-> ControleFuncionarios().ListarFuncionarios()
        form.addRow(ListaFuncionarios)

        BtnConfirmar = QPushButton("Remover Funcionário")
        #BtnConfirmar.clicked.connect(lambda: self.ConfirmarAdd(InputNome, InputEmail, InputCargo))
        form.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(FormWidget)

    def edit(self)-> None:
        self.LimparConteudo()

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)
        ListaFuncionarios = QComboBox()
        self.ConstruirListaFUncionarios(ListaFuncionarios)
        #Inventario-> ControleFuncionarios().ListarFuncionarios()
        form.addRow(ListaFuncionarios)
        BtnConfirmar = QPushButton("Editar Funcionário")
        
        #BtnConfirmar.clicked.connect(lambda: self.ConfirmarAdd(InputNome, InputEmail, InputCargo))
        form.addRow(BtnConfirmar)

        self.ConteudoLayout.addWidget(FormWidget)