#region base projeto
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDateEdit, QFormLayout, QComboBox, QLineEdit,
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
)
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    root = Path(sys._MEIPASS)
else:
    root = Path(__file__).parent.parent

sys.path.insert(0, str(root))

from data.Inventario import ControleFuncionario
#endregion base projeto

CARGOS = ["operario", "gerente"]
STATUS = ["Ativo", "Inativo", "Férias", "Licença"]


class ControleFuncionariosUI(QWidget):
    def __init__(self, tipo, Historico, GerenciarFuncionarios, Reverter,
                 Gerenciar, Dashboard, Inventario):
        super().__init__()
        self.tipo         = tipo
        self.IrInventario = Inventario
        self.IrReverter   = Reverter

        self.BtnInventario            = QPushButton("Inventário")
        self.BtnAdd                   = QPushButton("Adicionar")
        self.BtnRem                   = QPushButton("Remover")
        self.BtnEdit                  = QPushButton("Editar")
        self.BtnReverter              = QPushButton("Reverter")
        self.BtnHistorico             = QPushButton("Histórico")
        self.BtnDashboard             = QPushButton("Dashboards")
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
        for btn in (
            self.BtnInventario, self.BtnAdd, self.BtnRem,
            self.BtnEdit, self.BtnReverter, self.BtnHistorico,
            self.BtnDashboard, self.BtnGerenciarFuncionarios,
        ):
            topo.addWidget(btn)

        self.Conteudo = QWidget()
        self.ConteudoLayout = QHBoxLayout(self.Conteudo)

        base = QVBoxLayout()
        base.addLayout(topo)
        base.addWidget(self.Conteudo)
        self.setLayout(base)


    def AtualizarTipo(self, tipo: str) -> None:
        self.tipo = tipo
        MapaBtn  = {"add": self.BtnAdd, "rem": self.BtnRem, "edit": self.BtnEdit}
        mapaAcao = {"add": self.add,    "rem": self.remove,  "edit": self.edit}
        for btn in MapaBtn.values():
            btn.setVisible(True)
        if tipo in MapaBtn:
            MapaBtn[tipo].setVisible(False)
            mapaAcao[tipo]()

    @staticmethod
    def PopularCombo(combo: QComboBox) -> None:
        """Preenche o combo com 'Nome (ID: x)' e guarda o id como userData."""
        combo.clear()
        for func in ControleFuncionario().ListarFuncionarios():
            combo.addItem(f"{func.Nome}  (ID: {func.id})", userData=func.id)

    def LimparConteudo(self) -> None:
        while self.ConteudoLayout.count():
            item = self.ConteudoLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.LimparLayout(item.layout())

    def LimparLayout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.LimparLayout(item.layout())

    @staticmethod
    def LblErro() -> QLabel:
        lbl = QLabel("")
        lbl.setStyleSheet("color: #ff4444;")
        return lbl

    def add(self) -> None:
        self.LimparConteudo()

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)

        InputNome  = QLineEdit()
        InputEmail = QLineEdit()
        InputCargo = QComboBox()
        InputCargo.addItems(CARGOS)
        InputData  = QDateEdit(calendarPopup=True)
        InputData.setDate(QDate.currentDate())
        LblErro = self.LblErro()

        form.addRow("Nome:",     InputNome)
        form.addRow("Email:",    InputEmail)
        form.addRow("Cargo:",    InputCargo)
        form.addRow("Admissão:", InputData)
        form.addRow(LblErro)

        BtnConfirmar = QPushButton("Adicionar Funcionário")
        BtnConfirmar.clicked.connect(
            lambda: self.ConfirmarAdd(InputNome, InputEmail, InputCargo, InputData, LblErro)
        )
        form.addRow(BtnConfirmar)
        self.ConteudoLayout.addWidget(FormWidget)

    def ConfirmarAdd(self, InputNome, InputEmail, InputCargo, InputData, LblErro) -> None:
        nome = InputNome.text().strip()
        if not nome:
            LblErro.setText("Nome obrigatório.")
            return
        ControleFuncionario().Contratar(
            nome=nome,
            email=InputEmail.text().strip(),
            cargo=InputCargo.currentText(),
            data_admissao=str(InputData.date().toPython()),
        )
        self.IrInventario()

    def remove(self) -> None:
        self.LimparConteudo()

        FormWidget = QWidget()
        form = QFormLayout(FormWidget)
        form.setSpacing(10)

        Combo   = QComboBox()
        self.PopularCombo(Combo)
        LblErro = self.LblErro()

        form.addRow("Funcionário:", Combo)
        form.addRow(LblErro)

        BtnConfirmar = QPushButton("Remover Funcionário")
        BtnConfirmar.clicked.connect(lambda: self.ConfirmarRemove(Combo, LblErro))
        form.addRow(BtnConfirmar)
        self.ConteudoLayout.addWidget(FormWidget)

    def ConfirmarRemove(self, combo: QComboBox, LblErro: QLabel) -> None:
        FuncionarioID = combo.currentData()          # int — id único, sem colisão por nome
        if FuncionarioID is None:
            LblErro.setText("Nenhum funcionário selecionado.")
            return
        ok = ControleFuncionario().Demitir(FuncionarioID)
        if ok:
            self.IrInventario()
        else:
            LblErro.setText("Erro: funcionário não encontrado.")

    def edit(self) -> None:
        self.LimparConteudo()

        container = QVBoxLayout()

        SelWidget = QWidget()
        selForm   = QFormLayout(SelWidget)
        selForm.setSpacing(10)

        self.ComboEdit = QComboBox()
        self.PopularCombo(self.ComboEdit)

        BtnCarregar = QPushButton("Carregar dados")
        BtnCarregar.clicked.connect(self.CarregarDadosEdicao)
        selForm.addRow("Funcionário:", self.ComboEdit)
        selForm.addRow(BtnCarregar)
        container.addWidget(SelWidget)

        self.EditWidget = QWidget()
        self.EditWidget.hide()
        editForm = QFormLayout(self.EditWidget)
        editForm.setSpacing(10)

        self.EditNome   = QLineEdit()
        self.EditEmail  = QLineEdit()
        self.EditCargo  = QComboBox()
        self.EditCargo.addItems(CARGOS)
        self.EditStatus = QComboBox()
        self.EditStatus.addItems(STATUS)
        self.LblErroEdit = self.LblErro()

        editForm.addRow("Nome:",   self.EditNome)
        editForm.addRow("Email:",  self.EditEmail)
        editForm.addRow("Cargo:",  self.EditCargo)
        editForm.addRow("Status:", self.EditStatus)
        editForm.addRow(self.LblErroEdit)

        BtnSalvar = QPushButton("Salvar alterações")
        BtnSalvar.clicked.connect(self.ConfirmarEdicao)
        editForm.addRow(BtnSalvar)

        container.addWidget(self.EditWidget)
        self.ConteudoLayout.addLayout(container)

    def CarregarDadosEdicao(self) -> None:
        FuncionarioID = self.ComboEdit.currentData()
        if FuncionarioID is None:
            return
        func = ControleFuncionario().BuscarId(FuncionarioID)   # nome correto no banco
        if not func:
            return

        self.EditNome.setText(func.Nome or "")
        self.EditEmail.setText(func.Email or "")

        idx = self.EditCargo.findText(func.Cargo or "")
        self.EditCargo.setCurrentIndex(idx if idx >= 0 else 0)

        idx = self.EditStatus.findText(func.Status or "")
        self.EditStatus.setCurrentIndex(idx if idx >= 0 else 0)

        self.LblErroEdit.setText("")
        self.EditWidget.show()

    def ConfirmarEdicao(self) -> None:
        FuncionarioID = self.ComboEdit.currentData()
        nome    = self.EditNome.text().strip()
        if not nome:
            self.LblErroEdit.setText("Nome obrigatório.")
            return
        ok = ControleFuncionario().Editar(
            id=FuncionarioID,
            nome=nome,
            email=self.EditEmail.text().strip(),
            cargo=self.EditCargo.currentText(),
            status=self.EditStatus.currentText(),
        )
        if ok:
            self.IrInventario()
        else:
            self.LblErroEdit.setText("Erro ao salvar alterações.")